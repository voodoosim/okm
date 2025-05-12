# ui/panels/log_panel.py
import customtkinter as ctk
from .base_panel import BasePanel
from datetime import datetime


class LogPanel(BasePanel):
    """로그 출력 및 관리 패널"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)  # 고정 높이 유지
        self.setup_ui()

    def setup_ui(self):
        """로그 패널 UI 설정"""
        # 헤더 영역
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        # 제목
        ctk.CTkLabel(
            header_frame,
            text="실시간 로그",
            font=("", 14, "bold")
        ).pack(side="left")

        # 로그 레벨 필터
        self.log_level_var = ctk.StringVar(value="ALL")
        level_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["ALL", "INFO", "ERROR", "DEBUG"],
            variable=self.log_level_var,
            width=70,
            height=25
        )
        level_menu.pack(side="right", padx=5)

        # 지우기 버튼
        ctk.CTkButton(
            header_frame,
            text="지우기",
            width=60,
            height=25,
            command=self.clear_logs
        ).pack(side="right", padx=5)

        # 로그 텍스트 영역
        self.log_textbox = ctk.CTkTextbox(
            self,
            state="disabled",
            font=("Consolas", 11),
            wrap="word"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def add_log(self, message: str, level: str = "INFO"):
        """로그 메시지 추가"""
        # 필터링 확인
        current_filter = self.log_level_var.get()
        if current_filter != "ALL" and current_filter != level:
            return

        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 레벨별 색상 설정
        color_map = {
            "INFO": "#FFFFFF",
            "ERROR": self.COLORS["error"],
            "DEBUG": "#888888",
            "SUCCESS": self.COLORS["success"]
        }
        color = color_map.get(level, "#FFFFFF")

        # 로그 추가
        formatted_message = f"[{timestamp}] [{level}] {message}\n"

        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", formatted_message)
        self.log_textbox.tag_add(level, "end-2l", "end-1l")
        self.log_textbox.tag_config(level, foreground=color)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def clear_logs(self):
        """로그 지우기"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
