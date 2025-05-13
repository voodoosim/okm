# ui/features/base_feature.py
import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseFeature(ABC):
    """모든 기능 모듈의 기본 클래스"""

    def __init__(self, parent_frame: ctk.CTkFrame, main_window):
        self.parent_frame = parent_frame
        self.main_window = main_window
        self.widgets = {}
        self.config = {}
        self.sending = False

        # 색상 테마
        self.COLORS = {
            "primary": "#2E8B57",
            "secondary": "#3CB371",
            "error": "#FF6B6B",
            "warning": "#FFD93D",
            "success": "#00FF00"
        }

    @abstractmethod
    def create_ui(self):
        """UI 생성 (구현 필수)"""
        pass

    @abstractmethod
    def get_user_input(self) -> Dict[str, Any]:
        """사용자 입력 수집 (구현 필수)"""
        pass

    @abstractmethod
    def start_sending(self):
        """전송 시작 (구현 필수)"""
        pass

    def stop_sending(self):
        """전송 중지"""
        self.sending = False
        self.show_log("전송 중지됨")

    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """입력값 검증"""
        # 기본 검증 - 하위 클래스에서 오버라이드 가능
        if not data.get('target_id'):
            return False, "대상 ID를 입력해주세요."
        return True, ""

    def get_selected_sessions(self):
        """메인 창에서 선택된 세션 목록 가져오기"""
        return self.main_window.get_selected_sessions()

    def show_log(self, message: str, level: str = "INFO"):
        """로그 출력"""
        self.main_window.add_log(message, level)

    def show_error(self, message: str):
        """에러 메시지 출력"""
        self.show_log(message, "ERROR")

    def show_info(self, message: str):
        """정보 메시지 출력"""
        self.show_log(message, "INFO")

    def create_common_controls(self, parent_frame: ctk.CTkFrame):
        """공통 컨트롤 생성"""
        # 대상 ID 입력
        id_frame = ctk.CTkFrame(parent_frame)
        id_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(id_frame, text="대상 ID:", anchor="w").pack(anchor="w", padx=5)
        self.widgets['target_id'] = ctk.CTkEntry(
            id_frame,
            placeholder_text="@username 또는 채팅 ID"
        )
        self.widgets['target_id'].pack(fill="x", padx=5, pady=(0, 5))

        # 채팅 타입 선택
        chat_type_frame = ctk.CTkFrame(id_frame)
        chat_type_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(chat_type_frame, text="채팅 타입:").pack(side="left", padx=5)
        self.widgets['chat_type'] = ctk.StringVar(value="auto")

        ctk.CTkRadioButton(
            chat_type_frame,
            text="자동 감지",
            variable=self.widgets['chat_type'],
            value="auto"
        ).pack(side="left", padx=5)

        ctk.CTkRadioButton(
            chat_type_frame,
            text="개인",
            variable=self.widgets['chat_type'],
            value="personal"
        ).pack(side="left", padx=5)

        ctk.CTkRadioButton(
            chat_type_frame,
            text="그룹",
            variable=self.widgets['chat_type'],
            value="group"
        ).pack(side="left", padx=5)

    def create_control_buttons(self, parent_frame: ctk.CTkFrame):
        """컨트롤 버튼 생성"""
        btn_frame = ctk.CTkFrame(parent_frame)
        btn_frame.pack(fill="x", padx=15, pady=10)

        # 전송 시작 버튼
        self.widgets['start_btn'] = ctk.CTkButton(
            btn_frame,
            text="전송 시작",
            height=40,
            width=120,
            command=self.start_sending
        )
        self.widgets['start_btn'].pack(side="left", padx=15, pady=15)

        # 전송 중지 버튼
        self.widgets['stop_btn'] = ctk.CTkButton(
            btn_frame,
            text="전송 중지",
            height=40,
            width=120,
            command=self.stop_sending
        )
        self.widgets['stop_btn'].pack(side="left", padx=5, pady=15)
