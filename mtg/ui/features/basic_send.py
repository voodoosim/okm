"""
기본 메시지 전송 기능 구현
단일 메시지를 선택된 세션으로 전송하는 기본 기능
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Optional, Callable
from ui.features.base_feature import BaseFeature


class BasicSendFeature(BaseFeature):
    """기본 메시지 전송 기능 클래스"""

    def __init__(self, parent, session_manager=None, message_sender=None):
        """
        Args:
            parent: 부모 위젯
            session_manager: 세션 관리자 인스턴스
            message_sender: 메시지 전송기 인스턴스
        """
        super().__init__(parent)
        self.session_manager = session_manager
        self.message_sender = message_sender
        self.selected_session = None
        self.setup_ui()

    def setup_ui(self):
        """UI 구성 요소 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 세션 선택 섹션
        self._create_session_section(main_frame)

        # 메시지 입력 섹션
        self._create_message_section(main_frame)

        # 전송 설정 섹션
        self._create_settings_section(main_frame)

        # 버튼 섹션
        self._create_button_section(main_frame)

    def _create_session_section(self, parent):
        """세션 선택 UI 구성"""
        # 세션 선택 프레임
        session_frame = ttk.LabelFrame(parent, text="세션 선택")
        session_frame.pack(fill=tk.X, pady=(0, 10))

        # 세션 콤보박스
        tk.Label(session_frame, text="활성 세션:").pack(anchor=tk.W, padx=5, pady=5)
        self.session_combo = ttk.Combobox(session_frame, state="readonly")
        self.session_combo.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.session_combo.bind('<<ComboboxSelected>>', self._on_session_select)

        # 세션 새로고침 버튼
        refresh_btn = ttk.Button(session_frame, text="세션 새로고침",
                                command=self._refresh_sessions)
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def _create_message_section(self, parent):
        """메시지 입력 UI 구성"""
        # 메시지 입력 프레임
        message_frame = ttk.LabelFrame(parent, text="메시지 입력")
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 메시지 텍스트 에어리어
        tk.Label(message_frame, text="전송할 메시지:").pack(anchor=tk.W, padx=5, pady=5)
        self.message_text = scrolledtext.ScrolledText(
            message_frame, height=8, wrap=tk.WORD
        )
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # 메시지 길이 라벨
        self.char_count_label = tk.Label(message_frame, text="0 / 4096 문자")
        self.char_count_label.pack(anchor=tk.E, padx=5)

        # 텍스트 변경 이벤트 바인딩
        self.message_text.bind('<KeyRelease>', self._update_char_count)

    def _create_settings_section(self, parent):
        """전송 설정 UI 구성"""
        # 설정 프레임
        settings_frame = ttk.LabelFrame(parent, text="전송 설정")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # 대상 설정
        target_frame = ttk.Frame(settings_frame)
        target_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(target_frame, text="전송 대상:").pack(side=tk.LEFT)
        self.target_type = tk.StringVar(value="username")
        ttk.Radiobutton(target_frame, text="사용자명",
                       variable=self.target_type, value="username").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(target_frame, text="전화번호",
                       variable=self.target_type, value="phone").pack(side=tk.LEFT, padx=5)

        # 대상 입력
        self.target_entry = ttk.Entry(settings_frame)
        self.target_entry.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 옵션 체크박스들
        options_frame = ttk.Frame(settings_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        self.silent_mode = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="무음 모드 (알림 없이 전송)",
                       variable=self.silent_mode).pack(anchor=tk.W)

        self.parse_mode = tk.StringVar(value="markdown")
        parse_frame = ttk.Frame(options_frame)
        parse_frame.pack(anchor=tk.W, pady=5)
        tk.Label(parse_frame, text="파싱 모드:").pack(side=tk.LEFT)
        ttk.Combobox(parse_frame, textvariable=self.parse_mode,
                    values=["markdown", "html", "plain"],
                    state="readonly", width=10).pack(side=tk.LEFT, padx=5)

    def _create_button_section(self, parent):
        """버튼 섹션 구성"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # 미리보기 버튼
        self.preview_btn = ttk.Button(button_frame, text="미리보기",
                                     command=self._preview_message)
        self.preview_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 전송 버튼
        self.send_btn = ttk.Button(button_frame, text="메시지 전송",
                                  command=self._send_message, style="Accent.TButton")
        self.send_btn.pack(side=tk.RIGHT)

        # 초기에는 전송 버튼 비활성화
        self.send_btn.config(state="disabled")

    def _refresh_sessions(self):
        """세션 목록 새로고침"""
        if not self.session_manager:
            messagebox.showerror("오류", "세션 매니저가 연결되지 않았습니다.")
            return

        try:
            # 세션 목록 가져오기
            sessions = self.session_manager.get_session_list()

            # 콤보박스 업데이트
            session_names = [f"{s['name']} ({s['username']})"
                           for s in sessions if s['status'] == 'active']
            self.session_combo['values'] = session_names

            if session_names:
                self.session_combo.current(0)
                self._on_session_select(None)
            else:
                messagebox.showwarning("경고", "활성화된 세션이 없습니다.")

        except Exception as e:
            messagebox.showerror("오류", f"세션 목록 로드 실패: {str(e)}")

    def _on_session_select(self, event):
        """세션 선택 이벤트 처리"""
        if self.session_combo.get():
            # 선택된 세션 이름 추출
            session_text = self.session_combo.get()
            self.selected_session = session_text.split(' (')[0]
            self._validate_form()

    def _update_char_count(self, event=None):
        """문자 수 업데이트"""
        text = self.message_text.get(1.0, tk.END)
        char_count = len(text.strip())
        self.char_count_label.config(text=f"{char_count} / 4096 문자")

        # 4096자 제한 (텔레그램 제한)
        if char_count > 4096:
            self.char_count_label.config(fg="red")
            self.send_btn.config(state="disabled")
        else:
            self.char_count_label.config(fg="black")
            self._validate_form()

    def _validate_form(self):
        """폼 검증 및 전송 버튼 활성화/비활성화"""
        # 조건 체크
        has_session = bool(self.selected_session)
        has_message = bool(self.message_text.get(1.0, tk.END).strip())
        has_target = bool(self.target_entry.get().strip())
        char_count_ok = len(self.message_text.get(1.0, tk.END).strip()) <= 4096

        # 모든 조건 만족시 전송 버튼 활성화
        if has_session and has_message and has_target and char_count_ok:
            self.send_btn.config(state="normal")
        else:
            self.send_btn.config(state="disabled")

    def _preview_message(self):
        """메시지 미리보기"""
        message = self.message_text.get(1.0, tk.END).strip()
        target = self.target_entry.get().strip()

        if not message:
            messagebox.showwarning("경고", "메시지를 입력해주세요.")
            return

        # 미리보기 창 생성
        preview_window = tk.Toplevel(self)
        preview_window.title("메시지 미리보기")
        preview_window.geometry("400x300")
        preview_window.transient(self)
        preview_window.grab_set()

        # 미리보기 내용
        preview_text = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, state="disabled")
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 미리보기 텍스트 구성
        preview_content = f"""세션: {self.selected_session or '선택되지 않음'}
대상: {target} ({self.target_type.get()})
파싱 모드: {self.parse_mode.get()}
무음 모드: {'예' if self.silent_mode.get() else '아니요'}

--- 메시지 내용 ---
{message}
"""

        preview_text.config(state="normal")
        preview_text.insert(1.0, preview_content)
        preview_text.config(state="disabled")

        # 닫기 버튼
        ttk.Button(preview_window, text="닫기",
                  command=preview_window.destroy).pack(pady=10)

    def _send_message(self):
        """메시지 전송 실행"""
        if not self._validate_form_data():
            return

        # 전송 확인 다이얼로그
        if not messagebox.askyesno("확인", "메시지를 전송하시겠습니까?"):
            return

        try:
            # 전송 버튼 비활성화
            self.send_btn.config(state="disabled", text="전송 중...")

            # 메시지 전송 파라미터 구성
            send_params = {
                'session_name': self.selected_session,
                'target': self.target_entry.get().strip(),
                'target_type': self.target_type.get(),
                'message': self.message_text.get(1.0, tk.END).strip(),
                'silent': self.silent_mode.get(),
                'parse_mode': self.parse_mode.get()
            }

            # 메시지 전송 (비동기 처리 필요)
            self._send_message_async(send_params)

        except Exception as e:
            messagebox.showerror("오류", f"메시지 전송 실패: {str(e)}")
            self.send_btn.config(state="normal", text="메시지 전송")

    def _validate_form_data(self) -> bool:
        """폼 데이터 검증"""
        if not self.selected_session:
            messagebox.showerror("오류", "세션을 선택해주세요.")
            return False

        if not self.message_text.get(1.0, tk.END).strip():
            messagebox.showerror("오류", "메시지를 입력해주세요.")
            return False

        if not self.target_entry.get().strip():
            messagebox.showerror("오류", "전송 대상을 입력해주세요.")
            return False

        return True

    def _send_message_async(self, params):
        """비동기 메시지 전송 (실제 구현은 message_sender와 연동)"""
        # TODO: message_sender와 연동하여 실제 전송 로직 구현
        # 현재는 데모용 시뮬레이션

        def simulate_send():
            import time
            time.sleep(2)  # 전송 시뮬레이션

            # UI 업데이트는 메인 스레드에서 실행
            self.after(0, self._send_complete, True, "메시지가 성공적으로 전송되었습니다.")

        # 백그라운드 스레드에서 전송 시뮬레이션
        import threading
        threading.Thread(target=simulate_send, daemon=True).start()

    def _send_complete(self, success: bool, message: str):
        """전송 완료 콜백"""
        # 전송 버튼 복원
        self.send_btn.config(state="normal", text="메시지 전송")

        if success:
            messagebox.showinfo("성공", message)
            # 성공시 메시지 텍스트 클리어
            self.message_text.delete(1.0, tk.END)
            self._update_char_count()
        else:
            messagebox.showerror("실패", message)

    def set_session_manager(self, session_manager):
        """세션 매니저 설정"""
        self.session_manager = session_manager
        self._refresh_sessions()

    def set_message_sender(self, message_sender):
        """메시지 전송기 설정"""
        self.message_sender = message_sender


# 테스트 및 사용 예제
if __name__ == "__main__":
    # 테스트용 애플리케이션
    class MockSessionManager:
        def get_session_list(self):
            return [
                {"name": "1234567890", "username": "test_user", "phone": "...7890", "status": "active"},
                {"name": "0987654321", "username": "demo_user", "phone": "...4321", "status": "inactive"}
            ]

    root = tk.Tk()
    root.title("Basic Send Feature Test")
    root.geometry("600x700")

    # 스타일 설정
    style = ttk.Style()
    style.theme_use('clam')

    # 기본 전송 기능 테스트
    basic_send = BasicSendFeature(root)
    basic_send.pack(fill=tk.BOTH, expand=True)

    # 목업 세션 매니저 연결
    basic_send.set_session_manager(MockSessionManager())

    root.mainloop()
