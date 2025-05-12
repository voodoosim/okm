import customtkinter as ctk
import random
import time
from tkinter import messagebox
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ...main_window import TelegramMultiControlGUI

from .base_message_tab import MessageTab

class SpamModeTab(MessageTab):
    def __init__(self, parent: 'TelegramMultiControlGUI') -> None:
        super().__init__(parent)
        self.words_entries: List[ctk.CTkEntry] = []
        self.create()

    def create(self) -> None:
        """도배모드 탭 생성"""
        self.tab = self.parent.tabview.tab("도배모드")

        settings_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        self._create_common_settings(settings_frame, include_count=False, chat_type_default="group")

        words_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        words_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(words_frame, text="도배 단어 (2~4개):").pack(anchor="w", padx=10, pady=5)
        for i in range(4):
            entry = ctk.CTkEntry(words_frame, width=200)
            entry.pack(anchor="w", padx=10, pady=2)
            self.words_entries.append(entry)

        send_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start_sending).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="전송 중지", command=self.stop_sending).pack(side="left", padx=5)

    def start_sending(self) -> None:
        """메시지 전송 시작 (도배모드)"""
        target = self.target_entry.get().strip()
        chat_type = self.chat_type_var.get()

        words = [entry.get().strip() for entry in self.words_entries if entry.get().strip()]
        if not target or len(words) < 2 or len(words) > 4:
            messagebox.showerror("오류", "대상 ID와 2~4개의 단어를 입력해주세요.")
            return

        sessions = self._get_selected_sessions()
        if not sessions:
            return

        self.sending = True

        self._run_async_task(self._send_spam_mode_threaded, sessions, target, words, chat_type)

    async def _send_spam_mode_threaded(self, sessions: List[Dict[str, str]], target: str, words: List[str], chat_type: str) -> None:
        """스레드에서 도배모드 메시지 전송"""
        try:
            total_sent = 0
            while self.sending:
                num_words = random.randint(2, len(words))
                message = " ".join(random.sample(words, num_words))
                session = random.choice(sessions)
                await self.message_sender.send_bulk([session], target, 1, True, [message], chat_type)
                total_sent += 1
                self._update_status(f"진행률: {total_sent}개 전송됨")
                time.sleep(random.uniform(3, 10))
            if self.sending:
                self.root.after(0, lambda: messagebox.showinfo("완료", f"총 {total_sent}개 메시지가 전송되었습니다."))
        except Exception as e:
            self._handle_error(e, "도배모드 전송")
        finally:
            self.sending = False
            self._update_status("진행률: 0/0 (0.0%)")
            self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
            self.parent.log_panel.append_log("전송 완료")
