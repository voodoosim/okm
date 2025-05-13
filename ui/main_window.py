# ui/main_window.py 전체 수정
import customtkinter as ctk
from .panels.log_panel import LogPanel
from .panels.session_panel import SessionPanel
from .panels.function_panel import FunctionPanel
from .panels.main_panel import MainPanel
from .panels.terminal_panel import TerminalPanel
from ..core.session_manager import SessionManager
from ..core.message_sender import MessageSender
from ..core.rate_limiter import RateLimiter
from ..core.config_manager import ConfigManager
from ..utils.logger import EventLogger
from ..utils.monitor import Monitor
from ..core.dashboard import Dashboard

class TelegramMultiControlGUI(ctk.CTk):
    """메인 애플리케이션 창 - 5 Panel 레이아웃"""

    def __init__(self):
        super().__init__()

        # 설정 및 상태 색상
        self.STATUS_COLORS = {
            "active": "#00FF00",
            "inactive": "#FFA500",
            "unknown": "#FF0000"
        }

        self.setup_window()
        self.init_core_components()
        self.create_panels()
        self.layout_panels()
        self.setup_panel_connections()

    def setup_window(self):
        """기본 창 설정"""
        self.title("텔레그램 멀티컨트롤")
        self.geometry("1200x800")
        self.resizable(True, True)

    def init_core_components(self):
        """핵심 컴포넌트 초기화"""
        try:
            # 설정 매니저 초기화
            self.config_manager = ConfigManager()
            self.config = self.config_manager.config

            # 세션 매니저 초기화
            self.session_manager = SessionManager()

            # Rate Limiter 초기화
            self.rate_limiter = RateLimiter(
                self.config["rate_limits"]["daily_per_account"],
                self.config["rate_limits"]["hourly_per_account"],
                self.config["rate_limits"]["personal_min_delay"],
                self.config["rate_limits"]["personal_max_delay"],
                self.config["rate_limits"]["group_min_delay"],
                self.config["rate_limits"]["group_max_delay"],
                self.config["rate_limits"]["flood_wait_buffer"]
            )

            # 로깅 및 모니터링 초기화
            self.event_logger = EventLogger(self.config["app_settings"]["log_dir"])
            self.monitor = Monitor(
                self.config["app_settings"]["log_dir"],
                self.config["app_settings"]["report_dir"]
            )
            self.dashboard = Dashboard()

            # 메시지 sender 초기화
            self.message_sender = MessageSender(
                self.config["app_settings"]["session_dir"],
                self.config["api_settings"]["api_id"],
                self.config["api_settings"]["api_hash"],
                self.rate_limiter,
                self.event_logger,
                self.dashboard
            )

        except Exception as e:
            print(f"컴포넌트 초기화 오류: {e}")
            raise

    def create_panels(self):
        """5개 패널 생성"""
        self.log_panel = LogPanel(self, height=120)
        self.session_panel = SessionPanel(self, width=220)
        self.function_panel = FunctionPanel(self, width=150)
        self.main_panel = MainPanel(self)
        self.terminal_panel = TerminalPanel(self, height=150)

    def layout_panels(self):
        """5-Panel 레이아웃 배치"""
        # 상단: 로그
        self.log_panel.pack(fill="x", padx=5, pady=(5, 2))

        # 중간 프레임 생성
        middle_frame = ctk.CTkFrame(self, corner_radius=0)
        middle_frame.pack(fill="both", expand=True, padx=5, pady=2)

        # 좌측: 세션
        self.session_panel.pack(side="left", fill="y", padx=(0, 2), in_=middle_frame)

        # 우측: 기능
        self.function_panel.pack(side="right", fill="y", padx=(2, 0), in_=middle_frame)

        # 가운데: 메인
        self.main_panel.pack(side="left", fill="both", expand=True, padx=2, in_=middle_frame)

        # 하단: 터미널
        self.terminal_panel.pack(fill="x", padx=5, pady=(2, 5))

    def setup_panel_connections(self):
        """패널 간 연동 설정"""
        # 기능 패널의 변경 이벤트를 메인 패널에 연결
        self.function_panel.set_function_change_callback(self.main_panel.switch_content)

        # 모든 패널이 로그 패널을 사용할 수 있도록 설정
        self.session_panel.log_panel = self.log_panel
        self.function_panel.log_panel = self.log_panel
        self.main_panel.log_panel = self.log_panel
        self.terminal_panel.log_panel = self.log_panel

        # 터미널 패널이 다른 패널의 상태에 접근할 수 있도록 설정
        self.terminal_panel.parent = self

        # 세션 패널에 SessionManager 연결
        self.session_panel.set_session_manager(self.session_manager)

        # 터미널 패널에 SessionManager와 MessageSender 연결
        self.terminal_panel.set_session_manager(self.session_manager)
        self.terminal_panel.set_message_sender(self.message_sender)

    def get_selected_sessions(self):
        """세션 패널에서 선택된 세션 목록 반환"""
        return self.session_panel.get_selected_sessions()

    def switch_main_content(self, feature_name: str):
        """메인 패널 내용 전환 (외부 호출용)"""
        self.main_panel.switch_content(feature_name)

    def add_log(self, message: str, level: str = "INFO"):
        """로그 패널에 메시지 추가 (외부 호출용)"""
        self.log_panel.add_log(message, level)

    def create_new_session(self):
        """새 세션 생성 다이얼로그"""
        # 간단한 입력 다이얼로그
        dialog = ctk.CTkToplevel(self)
        dialog.title("새 세션 생성")
        dialog.geometry("350x180")
        dialog.transient(self)
        dialog.grab_set()

        # 제목
        ctk.CTkLabel(
            dialog,
            text="새 텔레그램 세션 생성",
            font=("", 16, "bold")
        ).pack(pady=15)

        # 전화번호 입력
        ctk.CTkLabel(dialog, text="전화번호:").pack()
        phone_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="+821234567890",
            width=250
        )
        phone_entry.pack(pady=10)
        phone_entry.focus()

        # 버튼 프레임
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=15)

        def create_session():
            phone = phone_entry.get().strip()
            if not phone:
                return

            try:
                result = self.session_manager.create_new_session(phone)
                if result['success']:
                    dialog.destroy()
                    self.add_log(f"새 세션 생성 성공: {result['session_name']}")
                    self.session_panel.refresh_sessions()
                else:
                    ctk.messagebox.showerror("오류", f"세션 생성 실패: {result['error']}")
            except Exception as e:
                ctk.messagebox.showerror("오류", f"세션 생성 중 오류: {str(e)}")

        ctk.CTkButton(
            btn_frame,
            text="생성",
            command=create_session
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="취소",
            command=dialog.destroy
        ).pack(side="right")

if __name__ == "__main__":
    app = TelegramMultiControlGUI()
    app.mainloop()
