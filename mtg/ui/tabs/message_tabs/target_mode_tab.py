import customtkinter as ctk
from tkinter import messagebox
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ...main_window import TelegramMultiControlGUI

from .base_message_tab import MessageTab

class TargetModeTab(MessageTab):
    def __init__(self, parent: 'TelegramMultiControlGUI') -> None:
        super().__init__(parent)
        self.create()

    def create(self) -> None:
        """목표치 모드 탭 생성"""
        self.tab = self.parent.tabview.tab("목표치 모드")

        settings_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        self._create_common_settings(settings_frame)

        self._create_message_frame(self.tab)

        send_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start_sending).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="전송 중지", command=self.stop_sending).pack(side="left", padx=5)

    def start_sending(self) -> None:
        """메시지 전송 시작 (목표치 모드)"""
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

        distribution = self.distribute_messages(sessions, count)

        self._run_async_task(self._send_target_mode_threaded, distribution, target, message, chat_type)

    async def _send_target_mode_threaded(self, distribution: List[tuple[Dict[str, str], int]], target: str, message: str, chat_type: str) -> None:
        """스레드에서 목표치 모드 메시지 전송"""
        try:
            total_sent = 0
            for session, num_messages in distribution:
                if not self.sending:
                    break
                await self.message_sender.send_bulk([session], target, num_messages, True, [message], chat_type)
                total_sent += num_messages
                self._update_status(f"진행률: {total_sent}/{sum(num for _, num in distribution)} ({total_sent/sum(num for _, num in distribution)*100:.1f}%)")
            if self.sending:
                self.root.after(0, lambda: messagebox.showinfo("완료", f"총 {total_sent}개 메시지가 전송되었습니다."))
        except Exception as e:
            self._handle_error(e, "목표치 모드 전송")
        finally:
            self.sending = False
            self._update_status("진행률: 0/0 (0.0%)")
            self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
            self.parent.log_panel.append_log("전송 완료")
