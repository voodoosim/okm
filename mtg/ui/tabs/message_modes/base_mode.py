import customtkinter as ctk
import tkinter as tk
from abc import ABC, abstractmethod

class ModeMetadata:
    def __init__(self, name, description, icon="📨", category="일반"):
        self.name = name
        self.description = description
        self.icon = icon
        self.category = category

class BaseMode(ABC):
    def __init__(self, parent):
        self.parent = parent
        self.tab = None
        self.sending = False
        self.target_entry = None
        self.chat_type_var = None
        self.message_text = None

    @classmethod
    @abstractmethod
    def get_metadata(cls):
        """모드 메타데이터 반환"""
        pass

    @abstractmethod
    def create_ui(self, tab):
        """UI 생성"""
        pass

    @abstractmethod
    def start_sending(self):
        """전송 시작"""
        pass

    def get_selected_accounts(self):
        """선택된 계정 리스트 반환 (공통 메서드)"""
        return self.parent.get_selected_accounts()

    def get_target_group_id(self):
        """대상 그룹 ID 반환 (공통 메서드)"""
        if self.target_entry:
            return self.target_entry.get().strip()
        return ""

    def create_common_settings(self, parent):
        """공통 설정 UI 생성"""
        settings_frame = ctk.CTkFrame(parent, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=10)

        # 대상 ID
        ctk.CTkLabel(settings_frame, text="대상 ID:").grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.target_entry = ctk.CTkEntry(settings_frame, width=400)
        self.target_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=10)

        # 채팅 타입
        ctk.CTkLabel(settings_frame, text="채팅 타입:").grid(row=1, column=0, sticky="w", pady=5, padx=10)
        self.chat_type_var = tk.StringVar(value="auto")
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=self.chat_type_var, value="auto").pack(side="left")
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=self.chat_type_var, value="personal").pack(side="left", padx=10)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=self.chat_type_var, value="group").pack(side="left")

        return settings_frame

    def create_message_frame(self, parent):
        """메시지 입력 프레임 생성"""
        message_frame = ctk.CTkFrame(parent, corner_radius=8)
        message_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(message_frame, text="메시지 내용:").pack(anchor="w", padx=10, pady=5)
        self.message_text = ctk.CTkTextbox(message_frame, height=100)
        self.message_text.pack(fill="both", expand=True, padx=10, pady=5)

        return message_frame
