# ui/panels/main_panel.py
import customtkinter as ctk
from .base_panel import BasePanel
from typing import Dict,  Any  # Any 추가
import importlib

class MainPanel(BasePanel):
    """메인 컨텐츠 패널 - 동적 기능 UI 영역"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_feature = None
        self.feature_instances: Dict[str, Any] = {}
        self.setup_ui()

    def setup_ui(self):
        """메인 패널 UI 설정"""
        # 컨텐츠 영역
        self.content_frame = ctk.CTkFrame(self, corner_radius=8)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 환영 메시지
        self.create_welcome_ui()

    def create_welcome_ui(self):
        """환영 화면 생성"""
        welcome_frame = ctk.CTkFrame(self.content_frame)
        welcome_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            welcome_frame,
            text="🚀 텔레그램 멀티컨트롤",
            font=("", 32, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            welcome_frame,
            text="우측에서 사용할 기능을 선택해주세요",
            font=("", 16),
            text_color="gray"
        ).pack()

    def switch_content(self, feature_name: str):
        """컨텐츠 영역 전환"""
        # 기존 컨텐츠 제거
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # 새 기능 컨텐츠 로드
        try:
            self._load_feature_ui(feature_name)
            self.current_feature = feature_name
            self.show_info(f"기능 UI 로드 완료: {feature_name}")
        except Exception as e:
            self.show_error(f"기능 UI 로드 실패: {feature_name} - {str(e)}")
            self.create_error_ui(feature_name, str(e))

    def _load_feature_ui(self, feature_name: str):
        """기능별 UI 동적 로드"""
        # feature_name을 모듈명으로 변환
        module_map = {
            "기본 전송": "basic_send",
            "목표치 모드": "target_mode",
            "토스 모드": "toss_mode",
            "도배 모드": "spam_mode",
            "대화 모드": "conversation_mode",
            "대시보드": "dashboard",
            "통계": "stats"
        }

        module_name = module_map.get(feature_name)
        if not module_name:
            raise ValueError(f"알 수 없는 기능: {feature_name}")

        # 모듈 동적 import
        try:
            module = importlib.import_module(f"ui.features.{module_name}")
            feature_class = getattr(module, f"{module_name.title().replace('_', '')}Feature")

            # 인스턴스 생성 또는 재사용
            if feature_name not in self.feature_instances:
                self.feature_instances[feature_name] = feature_class(self.content_frame, self.parent)

            # UI 생성
            feature_instance = self.feature_instances[feature_name]
            feature_instance.create_ui()

        except ImportError:
            # 모듈이 없으면 기본 UI 생성
            self.create_default_ui(feature_name)
        except Exception as e:
            raise Exception(f"모듈 로드 오류: {str(e)}")

    def create_default_ui(self, feature_name: str):
        """기본 UI 생성 (모듈이 없는 경우)"""
        # 기본 UI 매핑
        ui_creators = {
            "기본 전송": self._create_basic_send_ui,
            "목표치 모드": self._create_target_mode_ui,
            "토스 모드": self._create_toss_mode_ui,
            "도배 모드": self._create_spam_mode_ui,
            "대화 모드": self._create_conversation_mode_ui,
            "대시보드": self._create_dashboard_ui,
            "통계": self._create_stats_ui
        }

        creator = ui_creators.get(feature_name)
        if creator:
            creator()
        else:
            self.create_coming_soon_ui(feature_name)

    def create_error_ui(self, feature_name: str, error_message: str):
        """오류 UI 생성"""
        error_frame = ctk.CTkFrame(self.content_frame)
        error_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            error_frame,
            text="⚠️ 오류",
            font=("", 24, "bold"),
            text_color=self.COLORS["error"]
        ).pack(pady=20)

        ctk.CTkLabel(
            error_frame,
            text=f"기능: {feature_name}",
            font=("", 16)
        ).pack()

        ctk.CTkLabel(
            error_frame,
            text=f"오류: {error_message}",
            font=("", 12),
            text_color=self.COLORS["error"]
        ).pack(pady=10)

        ctk.CTkButton(
            error_frame,
            text="다시 시도",
            command=lambda: self.switch_content(feature_name)
        ).pack(pady=20)

    def create_coming_soon_ui(self, feature_name: str):
        """준비 중 UI 생성"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="🚧 준비 중...",
            font=("", 28)
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text=f"{feature_name} 기능은 곧 추가될 예정입니다.",
            font=("", 14),
            text_color="gray"
        ).pack()

    # 임시 UI 생성 메서드들 (나중에 별도 모듈로 분리)
    def _create_basic_send_ui(self):
        """기본 전송 UI"""
        main_frame = ctk.CTkFrame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 제목
        ctk.CTkLabel(
            main_frame,
            text="📤 기본 메시지 전송",
            font=("", 18, "bold")
        ).pack(pady=15)

        # 설정 영역
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=20, pady=10)

        # 대상 ID
        ctk.CTkLabel(settings_frame, text="대상 ID:", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        target_entry = ctk.CTkEntry(settings_frame, placeholder_text="@username 또는 채팅 ID")
        target_entry.pack(fill="x", padx=15, pady=(0, 15))

        # 채팅 타입
        chat_type_frame = ctk.CTkFrame(settings_frame)
        chat_type_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(chat_type_frame, text="채팅 타입:").pack(side="left", padx=10)
        chat_type_var = ctk.StringVar(value="auto")
        ctk.CTkRadioButton(chat_type_frame, text="자동 감지", variable=chat_type_var, value="auto").pack(side="left", padx=5)
        ctk.CTkRadioButton(chat_type_frame, text="개인", variable=chat_type_var, value="personal").pack(side="left", padx=5)
        ctk.CTkRadioButton(chat_type_frame, text="그룹", variable=chat_type_var, value="group").pack(side="left", padx=5)

        # 메시지 영역
        msg_frame = ctk.CTkFrame(main_frame)
        msg_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(msg_frame, text="메시지 내용:", anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        message_textbox = ctk.CTkTextbox(msg_frame, height=150)
        message_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 버튼 영역
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(btn_frame, text="전송 시작", height=40, width=120).pack(side="left", padx=15, pady=15)
        ctk.CTkButton(btn_frame, text="전송 중지", height=40, width=120).pack(side="left", padx=5, pady=15)

    def _create_target_mode_ui(self):
        """목표치 모드 UI"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="🎯 목표치 모드",
            font=("", 24, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text="총 채팅 수를 계정간 균등하게 분배하여 전송",
            font=("", 14),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            coming_frame,
            text="🚧 구현 중...",
            font=("", 16),
            text_color=self.COLORS["warning"]
        ).pack(pady=20)

    def _create_toss_mode_ui(self):
        """토스 모드 UI"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="⚡ 토스 모드",
            font=("", 24, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text="메시지를 단어별로 분할하여 여러 계정이 번갈아 전송",
            font=("", 14),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            coming_frame,
            text="🚧 구현 중...",
            font=("", 16),
            text_color=self.COLORS["warning"]
        ).pack(pady=20)

    def _create_spam_mode_ui(self):
        """도배 모드 UI"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="💨 도배 모드",
            font=("", 24, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text="랜덤 단어 조합으로 연속 전송",
            font=("", 14),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            coming_frame,
            text="🚧 구현 중...",
            font=("", 16),
            text_color=self.COLORS["warning"]
        ).pack(pady=20)

    def _create_conversation_mode_ui(self):
        """대화 모드 UI"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="💬 대화 모드",
            font=("", 24, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text="AI 기반 자동 대화 기능",
            font=("", 14),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            coming_frame,
            text="🚧 구현 중...",
            font=("", 16),
            text_color=self.COLORS["warning"]
        ).pack(pady=20)

    def _create_dashboard_ui(self):
        """대시보드 UI"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="📊 대시보드",
            font=("", 24, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text="실시간 상태 모니터링 및 대시보드",
            font=("", 14),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            coming_frame,
            text="🚧 구현 중...",
            font=("", 16),
            text_color=self.COLORS["warning"]
        ).pack(pady=20)

    def _create_stats_ui(self):
        """통계 UI"""
        coming_frame = ctk.CTkFrame(self.content_frame)
        coming_frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(
            coming_frame,
            text="📈 통계",
            font=("", 24, "bold")
        ).pack(expand=True)

        ctk.CTkLabel(
            coming_frame,
            text="전송 통계 및 리포트 기능",
            font=("", 14),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            coming_frame,
            text="🚧 구현 중...",
            font=("", 16),
            text_color=self.COLORS["warning"]
        ).pack(pady=20)
