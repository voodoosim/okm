import asyncio
import threading
import time
from tkinter import messagebox
import customtkinter as ctk

from ..base_mode import BaseMode, ModeMetadata

class BasicMode(BaseMode):
    @classmethod
    def get_metadata(cls):
        return ModeMetadata(
            name="기본 모드",
            description="계정별로 순차적으로 동일한 메시지를 전송합니다",
            icon="📨",
            category="기본"
        )

    def create_ui(self, tab):
        self.tab = tab

        # 모드 설명
        desc_frame = ctk.CTkFrame(tab, corner_radius=8)
        desc_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(desc_frame, text="📨 기본 모드", font=("", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(desc_frame, text="선택된 계정들이 같은 메시지를 순차적으로 전송합니다").pack(pady=5)

        # 공통 설정
        settings_frame = self.create_common_settings(tab)

        # 딜레이 설정
        ctk.CTkLabel(settings_frame, text="계정 간 딜레이(초):").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        self.delay_entry = ctk.CTkEntry(settings_frame, width=100)
        self.delay_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        self.delay_entry.insert(0, "1")

        # 메시지 프레임
        self.create_message_frame(tab)

        # 버튼 프레임
        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start_sending).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=self.delete_messages).pack(side="left", padx=5)

    def start_sending(self):
        """기본 모드 전송 시작"""
        target = self.get_target_group_id()
        message = self.message_text.get("1.0", "end").strip()
        chat_type = self.chat_type_var.get()
        delay = float(self.delay_entry.get())

        if not all([target, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True
        thread = threading.Thread(target=self._send_threaded, args=(sessions, target, message, chat_type, delay))
        thread.start()

    def _send_threaded(self, sessions, target, message, chat_type, delay):
        """스레드에서 전송"""
        async def send():
            try:
                for session in sessions:
                    if not self.sending:
                        break
                    await self.parent.message_sender.send_bulk([session], target, 1, True, [message], chat_type)
                    self.parent.log_panel.append_log(f"{session['name']} 계정으로 메시지 전송: {message}")
                    time.sleep(delay)

                if self.sending:
                    messagebox.showinfo("완료", "메시지 전송 완료")
            except Exception as e:
                messagebox.showerror("오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()

    def delete_messages(self):
        """메시지 삭제"""
        pass
