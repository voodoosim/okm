import customtkinter as ctk
import threading
import asyncio
from tkinter import messagebox

from ..base_mode import BaseMode, ModeMetadata

class TargetMode(BaseMode):
    def __init__(self, parent):
        super().__init__(parent)
        self.count_entry = None

    @classmethod
    def get_metadata(cls):
        return ModeMetadata(
            name="목표치 모드",
            description="총 채팅 수를 계정간 균등하게 분배합니다",
            icon="🎯",
            category="분배"
        )

    def create_ui(self, tab):
        """UI 생성"""
        self.tab = tab

        # 모드 설명
        desc_frame = ctk.CTkFrame(tab, corner_radius=8)
        desc_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(desc_frame, text="🎯 목표치 모드", font=("", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(desc_frame, text="총 채팅 수를 계정간 균등하게 분배하여 전송합니다").pack(pady=5)

        # 공통 설정
        settings_frame = self.create_common_settings(tab)

        # 목표 채팅 수 설정
        ctk.CTkLabel(settings_frame, text="목표 채팅 수:").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        self.count_entry = ctk.CTkEntry(settings_frame, width=100)
        self.count_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        self.count_entry.insert(0, "100")

        # 메시지 프레임
        self.create_message_frame(tab)

        # 버튼 프레임
        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start_sending).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=self.delete_messages).pack(side="left", padx=5)

    def start_sending(self):
        """목표치 모드 전송 시작"""
        target = self.get_target_group_id()
        message = self.message_text.get("1.0", "end").strip()
        chat_type = self.chat_type_var.get()
        count = self.count_entry.get().strip()

        if not all([target, message, count]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        try:
            count = int(count)
        except ValueError:
            messagebox.showerror("오류", "목표 채팅 수는 숫자여야 합니다.")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True

        # 계정별로 메시지 수 분배
        messages_per_account = count // len(sessions)
        remainder = count % len(sessions)
        distribution = []
        for i, session in enumerate(sessions):
            num_messages = messages_per_account + (1 if i < remainder else 0)
            distribution.append((session, num_messages))

        thread = threading.Thread(
            target=self._send_target_mode_threaded,
            args=(distribution, target, message, chat_type)
        )
        thread.start()

    def _send_target_mode_threaded(self, distribution, target, message, chat_type):
        """스레드에서 목표치 모드 메시지 전송"""
        async def send():
            try:
                total_sent = 0
                for session, num_messages in distribution:
                    if not self.sending:
                        break
                    await self.parent.message_sender.send_bulk([session], target, num_messages, True, [message], chat_type)
                    total_sent += num_messages
                    self.parent.log_panel.append_log(f"{session['name']} 계정: {num_messages}개 메시지 전송")

                if self.sending:
                    messagebox.showinfo("완료", f"총 {total_sent}개 메시지가 전송되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.parent.log_panel.append_log("전송 완료")

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()

    def delete_messages(self):
        """메시지 삭제"""
        # 삭제 기능 구현 예정
        messagebox.showinfo("알림", "메시지 삭제 기능은 아직 구현되지 않았습니다.")
