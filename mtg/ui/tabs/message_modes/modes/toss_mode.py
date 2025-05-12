import customtkinter as ctk
import random
import time
from tkinter import messagebox
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ....main_window import TelegramMultiControlGUI

from ...message_tabs.base_message_tab import MessageTab

class TossModeTab(MessageTab):
    def __init__(self, parent: 'TelegramMultiControlGUI') -> None:
        super().__init__(parent)
        self.create()

    def create(self) -> None:
        """토스모드 탭 생성"""
        self.tab = self.parent.tabview.tab("토스모드")

        settings_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        self._create_common_settings(settings_frame, include_count=False)

        self._create_message_frame(self.tab)

        send_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start_sending).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="전송 중지", command=self.stop_sending).pack(side="left", padx=5)

    def start_sending(self) -> None:
        """메시지 전송 시작 (토스모드)"""
        target = self.target_entry.get().strip()
        message = self.message_text.get("1.0", "end").strip()
        chat_type = self.chat_type_var.get()

        if not all([target, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        sessions = self._get_selected_sessions()
        if not sessions:
            return

        self.sending = True

        self._run_async_task(self._send_toss_mode_threaded, sessions, target, message, chat_type)

    async def _send_toss_mode_threaded(self, sessions: List[Dict[str, str]], target: str, message: str, chat_type: str) -> None:
        """스레드에서 토스모드 메시지 전송"""
        try:
            words = message.split()
            if not words:
                self.root.after(0, lambda: messagebox.showerror("오류", "메시지가 비어 있습니다."))
                return

            random.shuffle(sessions)
            total_words = len(words)
            for i in range(total_words):
                if not self.sending:
                    break
                session = sessions[i % len(sessions)]
                word = words[i]
                await self.message_sender.send_bulk([session], target, 1, True, [word], chat_type)
                time.sleep(random.uniform(0.5, 1.5))
            if self.sending:
                self.root.after(0, lambda: messagebox.showinfo("완료", f"총 {total_words}개 단어가 전송되었습니다."))
        except Exception as e:
            self._handle_error(e, "토스모드 전송")
        finally:
            self.sending = False
            self._update_status("진행률: 0/0 (0.0%)")
            self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
            self.parent.log_panel.append_log("전송 완료")
