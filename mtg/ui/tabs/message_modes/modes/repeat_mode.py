import asyncio
import threading
import random
import time

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from ..base_mode import BaseMode, ModeMetadata

class RepeatMode(BaseMode):
    @classmethod
    def get_metadata(cls):
        return ModeMetadata(
            name="반복 모드",
            description="설정된 라운드만큼 계정별로 메시지를 반복 전송합니다.",
            icon="🔄",
            category="기본"
        )

    def create(self, tab):
        """반복 모드 UI 생성"""
        self.tab = tab

        # 공통 설정
        self.create_common_settings(self.tab)

        # 반복 횟수 설정
        ctk.CTkLabel(self.tab, text="반복 횟수:").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        self.repeat_count_entry = ctk.CTkEntry(self.tab, width=100)
        self.repeat_count_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        self.repeat_count_entry.insert(0, "1")

        # 순서 설정
        ctk.CTkLabel(self.tab, text="순서:").grid(row=3, column=0, sticky="w", pady=5, padx=10)
        self.order_var = tk.StringVar(value="sequential")
        order_frame = ctk.CTkFrame(self.tab)
        order_frame.grid(row=3, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(order_frame, text="순차", variable=self.order_var, value="sequential").pack(side="left")
        ctk.CTkRadioButton(order_frame, text="랜덤", variable=self.order_var, value="random").pack(side="left", padx=10)

        # 계정 간 딜레이 설정
        ctk.CTkLabel(self.tab, text="계정 간 딜레이(초):").grid(row=4, column=0, sticky="w", pady=5, padx=10)
        self.delay_entry = ctk.CTkEntry(self.tab, width=100)
        self.delay_entry.grid(row=4, column=1, sticky="w", pady=5, padx=10)
        self.delay_entry.insert(0, "1")

        # 메시지 입력
        message_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        self.message_text = ctk.CTkTextbox(message_frame, height=100)
        self.message_text.pack(fill="both", expand=True, padx=10, pady=5)

        # 전송 버튼
        send_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=self.start).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=lambda: asyncio.run_coroutine_threadsafe(self.delete_my_messages(), asyncio.get_event_loop())).pack(side="left", padx=5)

    def start(self):
        """반복 모드 전송 시작"""
        target = self.target_entry.get().strip()
        chat_type = self.chat_type_var.get()
        message = self.message_text.get("1.0", "end").strip()
        try:
            repeat_count = int(self.repeat_count_entry.get())
            delay = float(self.delay_entry.get())
        except ValueError:
            messagebox.showerror("오류", "반복 횟수와 딜레이는 숫자여야 합니다.")
            return

        if not all([target, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True
        thread = threading.Thread(target=self._send_repeat_mode_threaded, args=(sessions, target, message, chat_type, repeat_count, self.order_var.get(), delay))
        thread.start()

    def _send_repeat_mode_threaded(self, sessions, target, message, chat_type, repeat_count, order, delay):
        async def send():
            try:
                total_sent = 0
                for round in range(repeat_count):
                    if not self.sending:
                        break
                    session_list = sessions.copy()
                    if order == "random":
                        random.shuffle(session_list)
                    for session in session_list:
                        if not self.sending:
                            break
                        await self.parent.parent.message_sender.send_bulk([session], target, 1, True, [message], chat_type)
                        total_sent += 1
                        self.parent.parent.log_panel.append_log(f"라운드 {round+1}: {session['name']} 계정으로 메시지 전송: {message}")
                        time.sleep(delay)
                if self.sending:
                    self.parent.root.after(0, messagebox.showinfo, "완료", f"총 {total_sent}개 메시지가 전송되었습니다.")
            except Exception as e:
                self.parent.root.after(0, messagebox.showerror, "오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.parent.root.after(0, lambda: self.parent.parent.status_bar.get_status_label().configure(text="진행률: 0/0 (0.0%)"))
                self.parent.root.after(0, lambda: self.parent.parent.status_bar.get_progress_bar().set(0))
                self.parent.root.after(0, lambda: self.parent.parent.log_panel.append_log("전송 완료"))

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()
