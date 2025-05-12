# ui/main_window.py 업데이트 (패널 간 연동 부분)
import customtkinter as ctk
from .panels.log_panel import LogPanel
from .panels.session_panel import SessionPanel
from .panels.function_panel import FunctionPanel
from .panels.main_panel import MainPanel
from .panels.terminal_panel import TerminalPanel

class TelegramMultiControlGUI(ctk.CTk):
    """메인 애플리케이션 창 - 5 Panel 레이아웃"""

    def __init__(self):
        super().__init__()
        self.setup_window()
        self.create_panels()
        self.layout_panels()
        self.setup_panel_connections()  # 패널 간 연동 설정

    def setup_window(self):
        """기본 창 설정"""
        self.title("텔레그램 멀티컨트롤")
        self.geometry("1200x800")
        self.resizable(True, True)

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

    def get_selected_sessions(self):
        """세션 패널에서 선택된 세션 목록 반환"""
        return self.session_panel.get_selected_sessions()

    def switch_main_content(self, feature_name: str):
        """메인 패널 내용 전환 (외부 호출용)"""
        self.main_panel.switch_content(feature_name)

    def add_log(self, message: str, level: str = "INFO"):
        """로그 패널에 메시지 추가 (외부 호출용)"""
        self.log_panel.add_log(message, level)

if __name__ == "__main__":
    app = TelegramMultiControlGUI()
    app.mainloop()
