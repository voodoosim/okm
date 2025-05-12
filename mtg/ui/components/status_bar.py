import customtkinter as ctk

from ..base_window import BaseWindow

class StatusBar(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.progress_bar = None
        self.status_label = None
        self.create()

    def create(self):
        """상단 상태 바 생성"""
        status_frame = ctk.CTkFrame(self.root, corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(status_frame, text="진행률: 0/0 (0.0%)")
        self.status_label.pack(side="right", padx=10)

    def get_progress_bar(self):
        """progress_bar 속성 반환"""
        return self.progress_bar

    def get_status_label(self):
        """status_label 속성 반환"""
        return self.status_label
