import asyncio
import threading

import customtkinter as ctk
from tkinter import messagebox

from ..base_window import BaseWindow

class SessionCreateDialog(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.top = ctk.CTkToplevel(self.root)
        self.top.title("새 세션 생성")
        self.top.geometry("400x250")

        self.name_entry = None
        self.phone_entry = None
        self.password_entry = None
        self.result = False

        self.create()

    def create(self):
        ctk.CTkLabel(self.top, text="세션 이름:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self.top, width=300)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.top, text="전화번호:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.phone_entry = ctk.CTkEntry(self.top, width=300)
        self.phone_entry.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.top, text="2차 인증 비밀번호:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(self.top, width=300, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.top, text="(없으면 비워두세요)", font=("", 10)).grid(row=3, column=1, padx=10, sticky="w")

        button_frame = ctk.CTkFrame(self.top)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ctk.CTkButton(button_frame, text="확인", command=self.ok_clicked).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="취소", command=self.cancel_clicked).pack(side="left", padx=5)

    def ok_clicked(self):
        """확인 버튼 클릭"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip() or None

        if not all([name, phone]):
            messagebox.showerror("오류", "세션 이름과 전화번호를 입력해주세요.")
            return

        # 비동기 세션 생성
        thread = threading.Thread(target=self._create_session_threaded, args=(name, phone, password))
        thread.start()

    def _create_session_threaded(self, name, phone, password):
        """스레드에서 비동기 세션 생성"""
        async def create():
            try:
                success = await self.session_manager.create_session(name, phone, password)
                if success:
                    self.result = True
                    self.top.after(0, self.top.destroy)
                else:
                    self.top.after(0, messagebox.showerror, "오류", "세션 생성에 실패했습니다.")
            except Exception as e:
                self.top.after(0, messagebox.showerror, "오류", f"세션 생성 중 오류: {str(e)}")

        # 새로운 이벤트 루프 생성
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(create())
        new_loop.close()

    def cancel_clicked(self):
        """취소 버튼 클릭"""
        self.top.destroy()
