import customtkinter as ctk
import time

from ..base_window import BaseWindow

class LogPanel(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.log_text = None
        self.create()

    def create(self):
        """실시간 로그 패널 생성"""
        log_frame = ctk.CTkFrame(self.root, corner_radius=8)
        log_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(log_frame, text="실시간 로그").pack(anchor="w", padx=10, pady=2)
        self.log_text = ctk.CTkTextbox(log_frame, height=100, state="disabled")
        self.log_text.pack(fill="x", padx=10, pady=5)

    def append_log(self, message):
        """새 로그 추가"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{time.strftime('%H:%M:%S')} {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
