import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...main_window import TelegramMultiControlGUI

from .base_message_tab import MessageTab

class BasicMessageTab(MessageTab):
    def __init__(self, parent: 'TelegramMultiControlGUI') -> None:
        super().__init__(parent)
        self.create()

    def create(self) -> None:
        """기본 메시지 전송 탭 생성"""
        self.tab = self.parent.tabview.tab("기본 메시지 전송")

        settings_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        self._create_common_settings(settings_frame)

        message_frame = self._create_message_frame(self.tab)

        self.same_message_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(message_frame, text="모든 계정에 동일 메시지 전송", variable=self.same_message_var).pack(anchor="w", padx=10, pady=5)

        send_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start_sending).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="전송 중지", command=self.stop_sending).pack(side="left", padx=5)

    def start_sending(self) -> None:
        """메시지 전송 시작"""
        target = self.target_entry.get().strip()
        count = self.count_entry.get().strip()
        message = self.message_text.get("1.0", "end").strip()
        chat_type = self.chat_type_var.get()

        if not all([target, count, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        try:
            count = int(count)
        except ValueError:
            messagebox.showerror("오류", "전송 횟수는 숫자여야 합니다.")
            return

        sessions = self._get_selected_sessions()
        if not sessions:
            return

        self.sending = True

        self._send_messages_threaded(sessions, target, count, self.same_message_var.get(), message, chat_type)
