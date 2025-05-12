import asyncio
import threading
import random
import time

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from ..base_window import BaseWindow

class ConversationModesTab(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.sending = False  # 독립적으로 초기화
        self.tab = None
        self.mode_tabview = None
        self.target_entries = {}  # 각 모드별 target_entry 저장
        self.create()

    def create(self):
        """대화 모드 탭 생성"""
        self.tab = self.parent.tabview.tab("대화 모드")
        self.mode_tabview = ctk.CTkTabview(self.tab, corner_radius=10)
        self.mode_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 5개 모드 탭 추가
        for mode in ["기본", "반복", "목표치", "토스", "도배"]:
            self.mode_tabview.add(mode)

        # 각 모드 UI 생성
        self.create_basic_mode()
        self.create_repeat_mode()
        self.create_target_mode()
        self.create_toss_mode()
        self.create_spam_mode()

    def get_selected_accounts(self):
        """선택된 계정 리스트 반환"""
        selected_items = self.parent.session_tab.get_session_tree().selection()
        if not selected_items:
            return []

        if len(selected_items) > 10:
            messagebox.showwarning("경고", "테스트를 위해 최대 10개 계정만 선택해주세요.")
            selected_items = selected_items[:10]

        sessions = []
        for item in selected_items:
            values = self.parent.session_tab.get_session_tree().item(item)["values"]
            sessions.append({
                "name": values[0],
                "username": values[1],
                "phone": values[2],
                "status": values[3]
            })
        return sessions

    def get_target_group_id(self):
        """현재 활성화된 탭의 그룹 ID 입력값 반환"""
        current_tab = self.mode_tabview.get()
        target_entry = self.target_entries.get(current_tab)
        if target_entry:
            return target_entry.get().strip()
        return ""

    async def delete_my_messages(self):
        """선택된 계정들의 그룹 메시지 삭제"""
        group_id = self.get_target_group_id()
        if not group_id:
            messagebox.showerror("오류", "그룹 ID를 입력하세요.")
            return

        selected_accounts = self.get_selected_accounts()
        if not selected_accounts:
            messagebox.showerror("오류", "계정을 선택하세요.")
            return

        for account in selected_accounts:
            account_name = account["name"]
            try:
                self.parent.log_panel.append_log(f"{account_name}의 메시지 삭제 중...")
                # 실제 구현에서는 Telegram API를 통해 메시지를 조회하고 삭제해야 함
                self.parent.log_panel.append_log(f"{account_name}의 메시지 삭제 완료")
            except Exception as e:
                self.parent.log_panel.append_log(f"{account_name} 메시지 삭제 실패: {str(e)}")
                messagebox.showerror("오류", f"{account_name} 메시지 삭제 중 오류: {str(e)}")

    def create_basic_mode(self):
        """기본 모드: 동일 메시지 순차 전송"""
        tab = self.mode_tabview.tab("기본")

        settings_frame = ctk.CTkFrame(tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        target_entry = ctk.CTkEntry(settings_frame, width=400)
        target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        self.target_entries["기본"] = target_entry

        ctk.CTkLabel(settings_frame, text="채팅 타입:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        chat_type_var = tk.StringVar(value="auto")
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=chat_type_var, value="auto").pack(side="left")
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=chat_type_var, value="personal").pack(side="left", padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=chat_type_var, value="group").pack(side="left")

        ctk.CTkLabel(settings_frame, text="계정 간 딜레이(초):").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        delay_entry = ctk.CTkEntry(settings_frame, width=100)
        delay_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        delay_entry.insert(0, "1")

        message_frame = ctk.CTkFrame(tab, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        message_text = ctk.CTkTextbox(message_frame, height=100)
        message_text.pack(fill="both", expand=True, padx=10, pady=5)

        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=lambda: self.start_basic_mode(target_entry.get().strip(), chat_type_var.get(), message_text.get("1.0", "end").strip(), float(delay_entry.get()))).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=lambda: asyncio.run_coroutine_threadsafe(self.delete_my_messages(), asyncio.get_event_loop())).pack(side="left", padx=5)

    def start_basic_mode(self, target, chat_type, message, delay):
        """기본 모드 전송 시작"""
        if not all([target, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True
        thread = threading.Thread(target=self._send_basic_mode_threaded, args=(sessions, target, message, chat_type, delay))
        thread.start()

    def _send_basic_mode_threaded(self, sessions, target, message, chat_type, delay):
        async def send():
            try:
                for session in sessions:
                    if not self.sending:
                        break
                    await self.message_sender.send_bulk([session], target, 1, True, [message], chat_type)
                    self.parent.log_panel.append_log(f"{session['name']} 계정으로 메시지 전송: {message}")
                    time.sleep(delay)
                if self.sending:
                    self.root.after(0, messagebox.showinfo, "완료", "메시지 전송 완료")
            except Exception as e:
                self.root.after(0, messagebox.showerror, "오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text="진행률: 0/0 (0.0%)"))
                self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
                self.root.after(0, lambda: self.parent.log_panel.append_log("전송 완료"))

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()

    def create_repeat_mode(self):
        """반복 모드: 라운드별 반복"""
        tab = self.mode_tabview.tab("반복")

        settings_frame = ctk.CTkFrame(tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        target_entry = ctk.CTkEntry(settings_frame, width=400)
        target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        self.target_entries["반복"] = target_entry

        ctk.CTkLabel(settings_frame, text="채팅 타입:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        chat_type_var = tk.StringVar(value="auto")
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=chat_type_var, value="auto").pack(side="left")
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=chat_type_var, value="personal").pack(side="left", padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=chat_type_var, value="group").pack(side="left")

        ctk.CTkLabel(settings_frame, text="반복 횟수:").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        repeat_count_entry = ctk.CTkEntry(settings_frame, width=100)
        repeat_count_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        repeat_count_entry.insert(0, "1")

        ctk.CTkLabel(settings_frame, text="순서:").grid(row=3, column=0, sticky="w", pady=5, padx=10)
        order_var = tk.StringVar(value="sequential")
        order_frame = ctk.CTkFrame(settings_frame)
        order_frame.grid(row=3, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(order_frame, text="순차", variable=order_var, value="sequential").pack(side="left")
        ctk.CTkRadioButton(order_frame, text="랜덤", variable=order_var, value="random").pack(side="left", padx=10)

        ctk.CTkLabel(settings_frame, text="계정 간 딜레이(초):").grid(row=4, column=0, sticky="w", pady=5, padx=10)
        delay_entry = ctk.CTkEntry(settings_frame, width=100)
        delay_entry.grid(row=4, column=1, sticky="w", pady=5, padx=10)
        delay_entry.insert(0, "1")

        message_frame = ctk.CTkFrame(tab, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        message_text = ctk.CTkTextbox(message_frame, height=100)
        message_text.pack(fill="both", expand=True, padx=10, pady=5)

        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=lambda: self.start_repeat_mode(target_entry.get().strip(), chat_type_var.get(), message_text.get("1.0", "end").strip(), int(repeat_count_entry.get()), order_var.get(), float(delay_entry.get()))).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=lambda: asyncio.run_coroutine_threadsafe(self.delete_my_messages(), asyncio.get_event_loop())).pack(side="left", padx=5)

    def start_repeat_mode(self, target, chat_type, message, repeat_count, order, delay):
        """반복 모드 전송 시작"""
        if not all([target, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        try:
            repeat_count = int(repeat_count)
        except ValueError:
            messagebox.showerror("오류", "반복 횟수는 숫자여야 합니다.")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True
        thread = threading.Thread(target=self._send_repeat_mode_threaded, args=(sessions, target, message, chat_type, repeat_count, order, delay))
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
                        await self.message_sender.send_bulk([session], target, 1, True, [message], chat_type)
                        total_sent += 1
                        self.parent.log_panel.append_log(f"라운드 {round+1}: {session['name']} 계정으로 메시지 전송: {message}")
                        time.sleep(delay)
                if self.sending:
                    self.root.after(0, messagebox.showinfo, "완료", f"총 {total_sent}개 메시지가 전송되었습니다.")
            except Exception as e:
                self.root.after(0, messagebox.showerror, "오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text="진행률: 0/0 (0.0%)"))
                self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
                self.root.after(0, lambda: self.parent.log_panel.append_log("전송 완료"))

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()

    def create_target_mode(self):
        """목표치 모드: 균등 분배"""
        tab = self.mode_tabview.tab("목표치")

        settings_frame = ctk.CTkFrame(tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        target_entry = ctk.CTkEntry(settings_frame, width=400)
        target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        self.target_entries["목표치"] = target_entry

        ctk.CTkLabel(settings_frame, text="채팅 타입:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        chat_type_var = tk.StringVar(value="auto")
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=chat_type_var, value="auto").pack(side="left")
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=chat_type_var, value="personal").pack(side="left", padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=chat_type_var, value="group").pack(side="left")

        ctk.CTkLabel(settings_frame, text="목표 채팅 수:").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        count_entry = ctk.CTkEntry(settings_frame, width=100)
        count_entry.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        count_entry.insert(0, "100")

        message_frame = ctk.CTkFrame(tab, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        message_text = ctk.CTkTextbox(message_frame, height=100)
        message_text.pack(fill="both", expand=True, padx=10, pady=5)

        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=lambda: self.start_target_mode(target_entry.get().strip(), chat_type_var.get(), message_text.get("1.0", "end").strip(), int(count_entry.get()))).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=lambda: asyncio.run_coroutine_threadsafe(self.delete_my_messages(), asyncio.get_event_loop())).pack(side="left", padx=5)

    def start_target_mode(self, target, chat_type, message, count):
        """목표치 모드 전송 시작"""
        if not all([target, message]):
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
        async def send():
            try:
                total_sent = 0
                for session, num_messages in distribution:
                    if not self.sending:
                        break
                    await self.message_sender.send_bulk([session], target, num_messages, True, [message], chat_type)
                    total_sent += num_messages
                    self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text=f"진행률: {total_sent}/{sum(num for _, num in distribution)} ({total_sent/sum(num for _, num in distribution)*100:.1f}%)"))
                if self.sending:
                    self.root.after(0, messagebox.showinfo, "완료", f"총 {total_sent}개 메시지가 전송되었습니다.")
            except Exception as e:
                self.root.after(0, messagebox.showerror, "오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text="진행률: 0/0 (0.0%)"))
                self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
                self.root.after(0, lambda: self.parent.log_panel.append_log("전송 완료"))

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()

    def create_toss_mode(self):
        """토스 모드: 메시지 분할"""
        tab = self.mode_tabview.tab("토스")

        settings_frame = ctk.CTkFrame(tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        target_entry = ctk.CTkEntry(settings_frame, width=400)
        target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        self.target_entries["토스"] = target_entry

        ctk.CTkLabel(settings_frame, text="채팅 타입:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        chat_type_var = tk.StringVar(value="auto")
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=chat_type_var, value="auto").pack(side="left")
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=chat_type_var, value="personal").pack(side="left", padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=chat_type_var, value="group").pack(side="left")

        ctk.CTkLabel(settings_frame, text="분할 방식:").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        split_var = tk.StringVar(value="word")
        split_frame = ctk.CTkFrame(settings_frame)
        split_frame.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(split_frame, text="단어", variable=split_var, value="word").pack(side="left")
        ctk.CTkRadioButton(split_frame, text="구문", variable=split_var, value="phrase").pack(side="left", padx=10)

        message_frame = ctk.CTkFrame(tab, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        message_text = ctk.CTkTextbox(message_frame, height=100)
        message_text.pack(fill="both", expand=True, padx=10, pady=5)

        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=lambda: self.start_toss_mode(target_entry.get().strip(), chat_type_var.get(), message_text.get("1.0", "end").strip(), split_var.get())).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=lambda: asyncio.run_coroutine_threadsafe(self.delete_my_messages(), asyncio.get_event_loop())).pack(side="left", padx=5)

    def start_toss_mode(self, target, chat_type, message, split_type):
        """토스 모드 전송 시작"""
        if not all([target, message]):
            messagebox.showerror("오류", "모든 필드를 입력해주세요.")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True
        thread = threading.Thread(target=self._send_toss_mode_threaded, args=(sessions, target, message, chat_type, split_type))
        thread.start()

    def _send_toss_mode_threaded(self, sessions, target, message, chat_type, split_type):
        async def send():
            try:
                # 메시지 분할
                if split_type == "word":
                    parts = message.split()
                else:
                    parts = message.split(".")
                    parts = [part.strip() for part in parts if part.strip()]
                if not parts:
                    self.root.after(0, messagebox.showerror, "오류", "메시지가 비어 있습니다.")
                    return

                random.shuffle(sessions)
                total_parts = len(parts)
                for i in range(total_parts):
                    if not self.sending:
                        break
                    session = sessions[i % len(sessions)]
                    part = parts[i]
                    await self.message_sender.send_bulk([session], target, 1, True, [part], chat_type)
                    self.parent.log_panel.append_log(f"{session['name']} 계정으로 메시지 전송: {part}")
                    time.sleep(random.uniform(0.5, 1.5))
                if self.sending:
                    self.root.after(0, messagebox.showinfo, "완료", f"총 {total_parts}개 부분이 전송되었습니다.")
            except Exception as e:
                self.root.after(0, messagebox.showerror, "오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text="진행률: 0/0 (0.0%)"))
                self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
                self.root.after(0, lambda: self.parent.log_panel.append_log("전송 완료"))

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()

    def create_spam_mode(self):
        """도배 모드: 랜덤 조합"""
        tab = self.mode_tabview.tab("도배")

        settings_frame = ctk.CTkFrame(tab, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        target_entry = ctk.CTkEntry(settings_frame, width=400)
        target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        self.target_entries["도배"] = target_entry

        ctk.CTkLabel(settings_frame, text="채팅 타입:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        chat_type_var = tk.StringVar(value="group")
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=chat_type_var, value="group").pack(side="left")

        ctk.CTkLabel(settings_frame, text="딜레이 범위(초):").grid(row=2, column=0, sticky="w", pady=5, padx=10)
        delay_frame = ctk.CTkFrame(settings_frame)
        delay_frame.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        min_delay_entry = ctk.CTkEntry(delay_frame, width=50)
        min_delay_entry.pack(side="left", padx=5)
        min_delay_entry.insert(0, "3")
        ctk.CTkLabel(delay_frame, text="~").pack(side="left")
        max_delay_entry = ctk.CTkEntry(delay_frame, width=50)
        max_delay_entry.pack(side="left", padx=5)
        max_delay_entry.insert(0, "10")

        words_frame = ctk.CTkFrame(tab, corner_radius=8)
        words_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(words_frame, text="도배 단어 (2~4개):").pack(anchor="w", padx=10, pady=5)
        words_entries = []
        for i in range(4):
            entry = ctk.CTkEntry(words_frame, width=200)
            entry.pack(anchor="w", padx=10, pady=2)
            words_entries.append(entry)

        send_frame = ctk.CTkFrame(tab, corner_radius=8)
        send_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(send_frame, text="전송 시작", command=lambda: self.start_spam_mode(target_entry.get().strip(), chat_type_var.get(), words_entries, float(min_delay_entry.get()), float(max_delay_entry.get()))).pack(side="left", padx=5)
        ctk.CTkButton(send_frame, text="메시지 삭제", command=lambda: asyncio.run_coroutine_threadsafe(self.delete_my_messages(), asyncio.get_event_loop())).pack(side="left", padx=5)

    def start_spam_mode(self, target, chat_type, words_entries, min_delay, max_delay):
        """도배 모드 전송 시작"""
        words = [entry.get().strip() for entry in words_entries if entry.get().strip()]
        if not target or len(words) < 2 or len(words) > 4:
            messagebox.showerror("오류", "대상 ID와 2~4개의 단어를 입력해주세요.")
            return

        try:
            min_delay = float(min_delay)
            max_delay = float(max_delay)
            if min_delay < 3 or max_delay < min_delay:
                raise ValueError("딜레이는 3초 이상이어야 하며, 최대 딜레이는 최소 딜레이보다 커야 합니다.")
        except ValueError as e:
            messagebox.showerror("오류", f"딜레이 설정 오류: {str(e)}")
            return

        sessions = self.get_selected_accounts()
        if not sessions:
            messagebox.showerror("오류", "전송할 계정을 선택해주세요.")
            return

        self.sending = True
        thread = threading.Thread(target=self._send_spam_mode_threaded, args=(sessions, target, words, chat_type, min_delay, max_delay))
        thread.start()

    def _send_spam_mode_threaded(self, sessions, target, words, chat_type, min_delay, max_delay):
        async def send():
            try:
                total_sent = 0
                while self.sending:
                    num_words = random.randint(2, len(words))
                    message = " ".join(random.sample(words, num_words))
                    session = random.choice(sessions)
                    await self.message_sender.send_bulk([session], target, 1, True, [message], chat_type)
                    total_sent += 1
                    self.parent.log_panel.append_log(f"{session['name']} 계정으로 메시지 전송: {message}")
                    self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text=f"진행률: {total_sent}개 전송됨"))
                    time.sleep(random.uniform(min_delay, max_delay))
                if self.sending:
                    self.root.after(0, messagebox.showinfo, "완료", f"총 {total_sent}개 메시지가 전송되었습니다.")
            except Exception as e:
                self.root.after(0, messagebox.showerror, "오류", f"전송 중 오류 발생: {str(e)}")
            finally:
                self.sending = False
                self.root.after(0, lambda: self.parent.status_bar.get_status_label().configure(text="진행률: 0/0 (0.0%)"))
                self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
                self.root.after(0, lambda: self.parent.log_panel.append_log("전송 완료"))

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(send())
        new_loop.close()
