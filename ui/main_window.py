"""
텔레그램 멀티컨트롤 메인 윈도우 - Grid 레이아웃 사용
"""
import customtkinter as ctk

# 백엔드 컴포넌트
from core.config_manager import ConfigManager
from core.session_manager import SessionManager
from core.message_sender import MessageSender
from core.rate_limiter import RateLimiter
from core.dashboard import Dashboard
from utils.logger import EventLogger
from utils.monitor import Monitor

# UI 패널
from .panels.log_panel import LogPanel
from .panels.session_panel import SessionPanel
from .panels.function_panel import FunctionPanel
from .panels.main_panel import MainPanel
from .panels.terminal_panel import TerminalPanel


class TelegramMultiControlGUI(ctk.CTk):
    """메인 애플리케이션 창 - Grid 레이아웃으로 5개 영역 구성"""

    def __init__(self):
        super().__init__()

        # 백엔드 초기화
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config

        if not self.config.get("api_settings", {}).get("api_id") or \
           not self.config.get("api_settings", {}).get("api_hash"):
            print("경고: API ID/Hash가 설정되지 않았습니다. 설정에서 추가해주세요.")

        self._init_backend_components()

        # UI 초기화
        self.setup_window()
        self.setup_grid()
        self.create_panels()
        self.layout_panels()
        self.setup_panel_connections()

    def _init_backend_components(self):
        """백엔드 컴포넌트 초기화"""
        rate_limits = self.config.get("rate_limits", {})
        app_settings = self.config.get("app_settings", {})
        api_settings = self.config.get("api_settings", {})

        self.rate_limiter = RateLimiter(
            daily_limit=rate_limits.get("daily_per_account", 500),
            hourly_limit=rate_limits.get("hourly_per_account", 100),
            personal_min_delay=rate_limits.get("personal_min_delay", 1.5),
            personal_max_delay=rate_limits.get("personal_max_delay", 3),
            group_min_delay=rate_limits.get("group_min_delay", 3),
            group_max_delay=rate_limits.get("group_max_delay", 6),
            flood_wait_buffer=rate_limits.get("flood_wait_buffer", 60),
            max_concurrent_accounts=rate_limits.get("max_concurrent_accounts", 5)
        )

        self.event_logger = EventLogger(app_settings.get("log_dir", "logs"))
        self.monitor = Monitor(
            app_settings.get("log_dir", "logs"),
            app_settings.get("report_dir", "reports")
        )
        self.dashboard = Dashboard()
        self.session_manager = SessionManager()

        if api_settings.get("api_id") and api_settings.get("api_hash"):
            self.message_sender = MessageSender(
                session_dir=app_settings.get("session_dir", "sessions"),
                api_id=api_settings["api_id"],
                api_hash=api_settings["api_hash"],
                rate_limiter=self.rate_limiter,
                event_logger=self.event_logger,
                dashboard=self.dashboard
            )
        else:
            self.message_sender = None

    def setup_window(self):
        """기본 창 설정"""
        self.title("텔레그램 멀티컨트롤")
        self.geometry("1200x800")
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        print(f"Window geometry: {self.winfo_geometry()}")

    def setup_grid(self):
        """창을 격자 레이아웃으로 구성"""
        self.grid_rowconfigure(0, weight=0)  # 로그 패널 (고정 높이)
        self.grid_rowconfigure(1, weight=1)  # 중단 패널 (확장)
        self.grid_rowconfigure(2, weight=0)  # 터미널 패널 (고정 높이)
        self.grid_columnconfigure(0, weight=0)  # 세션 패널 (고정 너비)
        self.grid_columnconfigure(1, weight=1)  # 메인 패널 (확장)
        self.grid_columnconfigure(2, weight=0)  # 기능 패널 (고정 너비)

    def create_panels(self):
        """5개 패널 생성"""
        print("Creating panels...")
        self.log_panel = LogPanel(self, height=120)
        print(f"Log panel created: {self.log_panel}")
        self.session_panel = SessionPanel(self, width=220)
        print(f"Session panel created: {self.session_panel}")
        self.function_panel = FunctionPanel(self, width=150)
        print(f"Function panel created: {self.function_panel}")
        self.main_panel = MainPanel(self)
        print(f"Main panel created: {self.main_panel}")
        self.terminal_panel = TerminalPanel(self, height=150)
        print(f"Terminal panel created: {self.terminal_panel}")

    def layout_panels(self):
        """격자 레이아웃으로 패널 배치"""
        print("Starting layout_panels...")
        self.log_panel.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=(5, 2))
        print("Log panel placed")
        self.session_panel.grid(row=1, column=0, sticky="ns", padx=(5, 2), pady=2)
        print("Session panel placed")
        self.function_panel.grid(row=1, column=2, sticky="ns", padx=(2, 5), pady=2)
        print("Function panel placed")
        self.main_panel.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        print("Main panel placed")
        self.terminal_panel.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=(2, 5))
        print("Terminal panel placed")

    def setup_panel_connections(self):
        """패널 간 연동 설정"""
        print("Setting up panel connections...")
        self.function_panel.set_function_change_callback(self.main_panel.switch_content)
        for panel in [self.session_panel, self.function_panel, self.main_panel, self.terminal_panel]:
            if hasattr(panel, 'log_panel'):
                panel.log_panel = self.log_panel
        self.terminal_panel.parent = self
        self.main_panel.session_manager = self.session_manager
        self.main_panel.message_sender = self.message_sender
        self.main_panel.config_manager = self.config_manager
        self.main_panel.rate_limiter = self.rate_limiter
        print("Panel connections setup complete")

    def get_selected_sessions(self) -> list:
        """세션 패널에서 선택된 세션 목록 반환"""
        return self.session_panel.get_selected_sessions()

    def switch_main_content(self, feature_name: str):
        """메인 패널 내용 전환"""
        self.main_panel.switch_content(feature_name)

    def add_log(self, message: str, level: str = "INFO"):
        """로그 패널에 메시지 추가"""
        self.log_panel.add_log(message, level)

    def create_new_session(self, phone_number: str) -> dict:
        """새 세션 생성 요청을 SessionManager로 전달"""
        if not self.session_manager:
            self.add_log("세션 매니저가 초기화되지 않았습니다.", "ERROR")
            return {"success": False, "session_name": "", "error": "SessionManager not initialized"}
        result = self.session_manager.create_new_session(phone_number)
        if result["success"]:
            self.add_log(f"새 세션 생성 성공: {result['session_name']}", "INFO")
            self.session_panel.refresh_sessions()  # 세션 목록 새로고침
        else:
            self.add_log(f"세션 생성 실패: {result['error']}", "ERROR")
        return result

    def show_settings(self):
        """설정 창 표시"""
        try:
            from ui.dialogs.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            if hasattr(dialog, 'top'):
                dialog.top.wait_window()
        except ImportError as e:
            self.add_log(f"설정 창 로드 실패: {e}", "ERROR")

    def show_help(self):
        """도움말 창 표시"""
        help_text = """텔레그램 멀티컨트롤 도움말

기본 사용법:
1. 세션 관리 - 좌측 패널에서 계정 추가/관리
2. 기능 선택 - 우측 패널에서 원하는 기능 선택
3. 설정 입력 - 중앙 패널에서 메시지, 대상 등 설정
4. 전송 시작 - 설정 완료 후 전송 버튼 클릭

터미널 명령어:
- help: 명령어 목록 표시
- sessions: 세션 목록 확인
- status: 현재 상태 확인
- test session: 세션 연결 테스트

주의사항:
- API 제한을 지키세요
- 계정 밴 방지를 위해 적절한 딜레이 설정
- 그룹 규칙을 준수하세요
"""
        self._show_dialog("도움말", help_text, "500x600")

    def show_about(self):
        """정보 창 표시"""
        about_text = """텔레그램 멀티컨트롤 v1.0

제작자: Grok & Claude 협업
GitHub: https://github.com/voodoosim/okm

기능:
- 다중 계정 관리
- 여러 전송 모드 지원
- 실시간 로그 및 모니터링
- 고급 설정 및 통계

라이선스: MIT
"""
        self._show_dialog("정보", about_text, "400x300")

    def _show_dialog(self, title: str, content: str, geometry: str = "400x300"):
        """공통 다이얼로그 표시 함수"""
        dialog_window = ctk.CTkToplevel(self)
        dialog_window.title(title)
        dialog_window.geometry(geometry)
        text_widget = ctk.CTkTextbox(dialog_window)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = TelegramMultiControlGUI()
    app.mainloop()
