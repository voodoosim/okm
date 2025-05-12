import threading
import asyncio
from typing import List, Dict, Optional, Callable, Awaitable, TYPE_CHECKING

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from ...base_window import BaseWindow

if TYPE_CHECKING:
    from ...main_window import TelegramMultiControlGUI

class MessageTab(BaseWindow):
    def __init__(self, parent: 'TelegramMultiControlGUI') -> None:
        super().__init__(parent)
        self._sending_lock: threading.Lock = threading.Lock()
        self._sending: bool = False
        self._active_threads: List[threading.Thread] = []
        self.target_entry: Optional[ctk.CTkEntry] = None
        self.count_entry: Optional[ctk.CTkEntry] = None
        self.chat_type_var: Optional[tk.StringVar] = None
        self.message_text: Optional[ctk.CTkTextbox] = None
        self.same_message_var: Optional[tk.BooleanVar] = None
        self.tab: Optional[ctk.CTkFrame] = None

    @property
    def sending(self) -> bool:
        with self._sending_lock:
            return self._sending

    @sending.setter
    def sending(self, value: bool) -> None:
        with self._sending_lock:
            self._sending = value

    def create(self) -> None:
        """탭 생성 (서브 클래스에서 구현)"""
        raise NotImplementedError("Subclasses must implement create method")

    def distribute_messages(self, sessions: List[Dict[str, str]], count: int) -> List[tuple[Dict[str, str], int]]:
        """계정별로 메시지 수를 균등하게 분배"""
        if not sessions:
            return []

        messages_per_account = count // len(sessions)
        remainder = count % len(sessions)
        distribution = []

        for i, session in enumerate(sessions):
            num_messages = messages_per_account + (1 if i < remainder else 0)
            distribution.append((session, num_messages))

        return distribution

    def start_sending(self) -> None:
        """메시지 전송 시작 (서브 클래스에서 구현)"""
        raise NotImplementedError("Subclasses must implement start_sending method")

    def stop_sending(self) -> None:
        """메시지 전송 중지"""
        if self.sending:
            self.message_sender.stop_sending()
            self.sending = False
            self._update_status("전송 중지됨")
            self.parent.log_panel.append_log("전송 중지됨")
            for thread in self._active_threads:
                if thread.is_alive():
                    thread.join(timeout=1.0)
            self._active_threads.clear()

    def _send_messages_threaded(self, sessions: List[Dict[str, str]], target: str, count: int, same_message: bool, message: str, chat_type: str) -> None:
        """스레드에서 비동기 메시지 전송 (기본 구현)"""
        async def send():
            try:
                messages = [message] if same_message else [f"{message} #{i+1}" for i in range(count)]
                await self.message_sender.send_bulk(sessions, target, count, same_message, messages, chat_type)
                self.root.after(0, lambda: messagebox.showinfo("완료", f"총 {count}개 메시지가 전송되었습니다."))
            except Exception as e:
                self._handle_error(e, "메시지 전송")
            finally:
                self.sending = False
                self._update_status("진행률: 0/0 (0.0%)")
                self.root.after(0, lambda: self.parent.status_bar.get_progress_bar().set(0))
                self.parent.log_panel.append_log("전송 완료")

        self._run_async_task(send)

    def _run_async_task(self, async_func: Callable[..., Awaitable[None]], *args, **kwargs) -> None:
        """비동기 작업을 별도 스레드에서 실행"""
        def run():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                new_loop.run_until_complete(async_func(*args, **kwargs))
            finally:
                new_loop.close()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self._active_threads.append(thread)

    def _handle_error(self, error: Exception, context: str = "작업") -> None:
        """공통 에러 처리"""
        error_msg = f"{context} 중 오류 발생: {str(error)}"
        self.parent.log_panel.append_log(error_msg)
        self.root.after(0, lambda: messagebox.showerror("오류", error_msg))

    def _update_status(self, text: str) -> None:
        """상태 업데이트 최적화"""
        if hasattr(self.parent, 'status_bar'):
            self.root.after(0, self.parent.status_bar.get_status_label().configure, text=text)

    def _create_common_settings(self, frame: ctk.CTkFrame, include_count: bool = True, chat_type_default: str = "auto") -> None:
        """공통 설정 UI 생성"""
        ctk.CTkLabel(frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.target_entry = ctk.CTkEntry(frame, width=400)
        self.target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)

        if include_count:
            ctk.CTkLabel(frame, text="전송 횟수:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
            self.count_entry = ctk.CTkEntry(frame, width=100)
            self.count_entry.grid(row=1, column=1, sticky="w", pady=5, padx=10)

        ctk.CTkLabel(frame, text="채팅 타입:").grid(row=2 if include_count else 1, column=0, sticky="w", pady=5, padx=10)
        self.chat_type_var = tk.StringVar(value=chat_type_default)
        chat_type_frame = ctk.CTkFrame(frame)
        chat_type_frame.grid(row=2 if include_count else 1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=self.chat_type_var, value="auto").pack(side="left")
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=self.chat_type_var, value="personal").pack(side="left", padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=self.chat_type_var, value="group").pack(side="left")

    def _create_message_frame(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """메시지 입력 프레임 생성"""
        message_frame = ctk.CTkFrame(parent, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        self.message_text = ctk.CTkTextbox(message_frame, height=100)
        self.message_text.pack(fill="both", expand=True, padx=10, pady=5)

        return message_frame

    def _get_selected_sessions(self) -> Optional[List[Dict[str, str]]]:
        """선택된 세션 반환"""
        if not hasattr(self.parent, 'session_tab') or not self.parent.session_tab:
            self._handle_error(Exception("세션 탭을 찾을 수 없습니다."), "세션 로드")
            return None

        session_tree = self.parent.session_tab.get_session_tree()
        if not session_tree:
            self._handle_error(Exception("세션 트리를 찾을 수 없습니다."), "세션 로드")
            return None

        selected_items = [session_tree.item(item) for item in session_tree.selection()]
        if not selected_items:
            self._handle_error(Exception("전송할 계정을 선택해주세요."), "세션 선택")
            return None

        if len(selected_items) > 10:
            self.root.after(0, lambda: messagebox.showwarning("경고", "테스트를 위해 최대 10개 계정만 선택해주세요."))
            selected_items = selected_items[:10]

        sessions = []
        for item in selected_items:
            values = item["values"]
            sessions.append({
                "name": values[0],
                "username": values[1],
                "phone": values[2],
                "status": values[3]
            })
        return sessions
