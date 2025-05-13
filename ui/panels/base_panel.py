# ui/panels/base_panel.py
import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Any

class BasePanel(ctk.CTkFrame, ABC):
    """모든 패널의 기본 클래스"""

    def __init__(self, parent: Any, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.setup_colors()

    def setup_colors(self):
        """패널별 색상 설정"""
        self.COLORS = {
            "primary": "#2E8B57",
            "secondary": "#3CB371",
            "background": "#121212",
            "surface": "#1E1E1E",
            "text": "#FFFFFF",
            "success": "#00FF00",
            "error": "#FF6B6B",
            "warning": "#FFD93D"
        }

    @abstractmethod
    def setup_ui(self):
        """각 패널의 UI 설정 (구현 필수)"""
        pass

    def show_log(self, message: str, level: str = "INFO"):
        """상위 창의 로그 패널에 메시지 표시"""
        if hasattr(self.parent, 'log_panel'):
            self.parent.log_panel.add_log(message, level)

    def show_error(self, message: str):
        """에러 메시지 표시"""
        self.show_log(message, "ERROR")

    def show_info(self, message: str):
        """정보 메시지 표시"""
        self.show_log(message, "INFO")
