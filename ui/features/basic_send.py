# ui/features/basic_send.py 수정
import customtkinter as ctk
from .base_feature import BaseFeature
from typing import Dict, Any
import threading
import time

class BasicSendFeature(BaseFeature):
    """기본 메시지 전송 기능"""

    def __init__(self, parent_frame: ctk.CTkFrame, main_window):
        super().__init__(parent_frame, main_window)
        self.session_manager = main_window.session_manager
        self.message_sender = main_window.message_sender

    def create_ui(self):
        """기본 전송 모드 UI 생성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.parent_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="📤 기본 메시지 전송",
            font=("", 18, "bold")
        )
        title_label.pack(pady=15)

        # 설명
        desc_label = ctk.CTkLabel(
            main_frame,
            text="선택된 계정들이 동일한 메시지를 순차적으로 전송합니다.",
            text_color="gray"
        )
        desc_label.pack(pady=5)

        # 설정 영역
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=20, pady=10)

        # 공통 컨트롤 생성
        self.create_common_controls(settings_frame)

        # 계정 간 딜레이 설정
        delay_frame = ctk.CTkFrame(settings_frame)
        delay_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(delay_frame, text="계정 간 딜레이:", anchor="w").pack(anchor="w", padx=5)
        self.widgets['delay'] = ctk.CTkEntry(delay_frame, placeholder_text="1.0 (초)")
        self.widgets['delay'].pack(fill="x", padx=5, pady=(0, 5))
        self.widgets['delay'].insert(0, "1.0")

        # 메시지 영역
        msg_frame = ctk.CTkFrame(main_frame)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(msg_frame, text="메시지 내용:", anchor="w").pack(anchor="w", padx=15, pady=(15, 5))
        self.widgets['message'] = ctk.CTkTextbox(msg_frame, height=150)
        self.widgets['message'].pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 컨트롤 버튼
        self.create_control_buttons(main_frame)

    def get_user_input(self) -> Dict[str, Any]:
        """사용자 입력 수집"""
        return {
            'target_id': self.widgets['target_id'].get().strip(),
            'chat_type': self.widgets['chat_type'].get(),
            'message': self.widgets['message'].get("1.0", "end").strip(),
            'delay': float(self.widgets['delay'].get() or "1.0")
        }

    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """입력값 검증"""
        valid, msg = super().validate_input(data)
        if not valid:
            return valid, msg

        if not data.get('message'):
            return False, "메시지 내용을 입력해주세요."

        return True, ""

    def start_sending(self):
        """전송 시작"""
        # 선택된 세션 확인
        sessions = self.get_selected_sessions()
        if not sessions:
            self.show_error("전송할 계정을 선택해주세요.")
            return

        # 입력값 수집 및 검증
        data = self.get_user_input()
        valid, error_msg = self.validate_input(data)
        if not valid:
            self.show_error(error_msg)
            return

        # 전송 상태 설정
        self.sending = True
        self.widgets['start_btn'].configure(state="disabled")
        self.widgets['stop_btn'].configure(state="normal")

        # 로그 출력
        self.show_info(f"기본 전송 시작: {len(sessions)}개 계정")

        # 실제 전송 (비동기)
        self._run_sending_task(sessions, data)

    def _run_sending_task(self, sessions, data):
        """백그라운드에서 메시지 전송"""
        def send_task():
            try:
                sent_count = 0
                total_count = len(sessions)

                for i, session_name in enumerate(sessions):
                    if not self.sending:
                        break

                    # 상태 업데이트
                    self.main_window.after(0,
                        lambda i=i: self.show_info(f"전송 중... ({i+1}/{total_count}) - {session_name}")
                    )

                    # 실제 전송 (현재는 시뮬레이션)
                    time.sleep(data['delay'])
                    sent_count += 1

                    # 진행률 업데이트
                    progress = (sent_count / total_count) * 100
                    self.main_window.after(0,
                        lambda p=progress: self.show_info(f"진행률: {p:.1f}% ({sent_count}/{total_count})")
                    )

                # 완료 처리
                if self.sending:
                    self.main_window.after(0,
                        lambda: self.show_info(f"✅ 전송 완료: {sent_count}개 계정")
                    )

            except Exception as e:
                self.main_window.after(0,
                    lambda: self.show_error(f"전송 오류: {str(e)}")
                )
            finally:
                self.main_window.after(0, self._reset_controls)

        # 백그라운드 스레드 시작
        thread = threading.Thread(target=send_task, daemon=True)
        thread.start()

    def _reset_controls(self):
        """컨트롤 상태 리셋"""
        self.sending = False
        self.widgets['start_btn'].configure(state="normal")
        self.widgets['stop_btn'].configure(state="disabled")
