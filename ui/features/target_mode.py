# ui/features/target_mode.py
import customtkinter as ctk
from .base_feature import BaseFeature
from typing import Dict, Any

class TargetModeFeature(BaseFeature):
    """목표치 모드 - 총 메시지 수를 계정별로 균등 분배"""

    def __init__(self, parent_frame: ctk.CTkFrame, main_window):
        super().__init__(parent_frame, main_window)

    def create_ui(self):
        """목표치 모드 UI 생성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.parent_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎯 목표치 모드",
            font=("", 18, "bold")
        )
        title_label.pack(pady=15)

        # 설명
        desc_label = ctk.CTkLabel(
            main_frame,
            text="총 메시지 수를 선택된 계정들에게 균등하게 분배하여 전송합니다.",
            text_color="gray"
        )
        desc_label.pack(pady=5)

        # 설정 영역
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=20, pady=10)

        # 공통 컨트롤 생성
        self.create_common_controls(settings_frame)

        # 목표 메시지 수
        target_frame = ctk.CTkFrame(settings_frame)
        target_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(target_frame, text="목표 메시지 수:", anchor="w").pack(anchor="w", padx=5)
        self.widgets['target_count'] = ctk.CTkEntry(target_frame, placeholder_text="예: 100")
        self.widgets['target_count'].pack(fill="x", padx=5, pady=(0, 5))

        # 분배 미리보기
        self.widgets['preview_label'] = ctk.CTkLabel(
            target_frame,
            text="",
            text_color="gray"
        )
        self.widgets['preview_label'].pack(anchor="w", padx=5)

        # 목표 수 변경 시 미리보기 업데이트
        self.widgets['target_count'].bind('<KeyRelease>', self._update_preview)

        # 메시지 영역
        msg_frame = ctk.CTkFrame(main_frame)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(msg_frame, text="메시지 내용:", anchor="w").pack(anchor="w", padx=15, pady=(15, 5))
        self.widgets['message'] = ctk.CTkTextbox(msg_frame, height=150)
        self.widgets['message'].pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 컨트롤 버튼
        self.create_control_buttons(main_frame)

        # 초기 미리보기 업데이트
        self._update_preview()

    def _update_preview(self, event=None):
        """메시지 분배 미리보기 업데이트"""
        try:
            count = int(self.widgets['target_count'].get() or "0")
            sessions = self.get_selected_sessions()

            if count > 0 and sessions:
                num_sessions = len(sessions)
                per_account = count // num_sessions
                remainder = count % num_sessions

                preview_text = f"계정별 분배: {per_account}개"
                if remainder > 0:
                    preview_text += f" (+{remainder}개 계정은 +1개)"
                preview_text += f" | 총 {num_sessions}개 계정"
            else:
                preview_text = "계정을 선택하고 목표 수를 입력하세요."

            self.widgets['preview_label'].configure(text=preview_text)
        except ValueError:  # int() 변환 실패 시
            self.widgets['preview_label'].configure(text="")
        except (AttributeError, KeyError) :  # 위젯 접근 오류 시
            self.widgets['preview_label'].configure(text="")

    def get_user_input(self) -> Dict[str, Any]:
        """사용자 입력 수집"""
        return {
            'target_id': self.widgets['target_id'].get().strip(),
            'chat_type': self.widgets['chat_type'].get(),
            'message': self.widgets['message'].get("1.0", "end").strip(),
            'target_count': int(self.widgets['target_count'].get() or "0")
        }

    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """입력값 검증"""
        valid, msg = super().validate_input(data)
        if not valid:
            return valid, msg

        if not data.get('message'):
            return False, "메시지 내용을 입력해주세요."

        if data.get('target_count', 0) <= 0:
            return False, "목표 메시지 수는 1 이상이어야 합니다."

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

        # 메시지 분배 계산
        distribution = self._calculate_distribution(sessions, data['target_count'])

        # 전송 상태 설정
        self.sending = True
        self.widgets['start_btn'].configure(state="disabled")
        self.widgets['stop_btn'].configure(state="normal")

        # 로그 출력
        self.show_info(f"목표치 모드 시작: 총 {data['target_count']}개 메시지를 {len(sessions)}개 계정에 분배")

        # TODO: Grok의 MessageSender와 연동하여 실제 전송 구현
        self._simulate_sending(distribution, data)

    def _calculate_distribution(self, sessions, total_count):
        """메시지 분배 계산"""
        distribution = []
        per_account = total_count // len(sessions)
        remainder = total_count % len(sessions)

        for i, session in enumerate(sessions):
            count = per_account + (1 if i < remainder else 0)
            distribution.append((session, count))

        return distribution

    def _simulate_sending(self, distribution, data):
        """전송 시뮬레이션 (임시)"""
        import threading
        import time

        def send_process():
            try:
                total_sent = 0
                for session, count in distribution:
                    if not self.sending:
                        break

                    self.show_info(f"{session}: {count}개 메시지 전송 시뮬레이션")
                    total_sent += count
                    time.sleep(0.5)  # 시뮬레이션 딜레이

                if self.sending:
                    self.show_info(f"✅ 목표치 달성: {total_sent}개 메시지 전송 완료")
            except Exception as e:
                self.show_error(f"전송 오류: {str(e)}")
            finally:
                self.sending = False
                # UI 스레드에서 안전하게 실행하기 위해 main_window.after 사용
                self.main_window.after(0, self._reset_controls)

        thread = threading.Thread(target=send_process, daemon=True)
        thread.start()

    def _reset_controls(self):
        """컨트롤 상태 리셋"""
        self.widgets['start_btn'].configure(state="normal")
        self.widgets['stop_btn'].configure(state="disabled")
