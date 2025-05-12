# ui/panels/function_panel.py
import customtkinter as ctk
from .base_panel import BasePanel
from typing import Callable, Optional

class FunctionPanel(BasePanel):
    """기능 선택 패널 - 우측 버튼 그룹"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)  # 고정 너비 유지
        self.function_buttons = {}
        self.current_function = None
        self.on_function_change: Optional[Callable] = None
        self.setup_ui()

    def setup_ui(self):
        """기능 패널 UI 설정"""
        # 헤더
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header_frame,
            text="기능 선택",
            font=("", 14, "bold")
        ).pack()

        # 기능 목록 정의
        self.functions = [
            {
                "name": "기본 전송",
                "icon": "📤",
                "description": "동일 메시지 순차 전송",
                "category": "전송"
            },
            {
                "name": "목표치 모드",
                "icon": "🎯",
                "description": "총 메시지 수 균등 분배",
                "category": "전송"
            },
            {
                "name": "토스 모드",
                "icon": "⚡",
                "description": "메시지 단어별 분할 전송",
                "category": "전송"
            },
            {
                "name": "도배 모드",
                "icon": "💨",
                "description": "랜덤 단어 조합 연속 전송",
                "category": "전송"
            },
            {
                "name": "대화 모드",
                "icon": "💬",
                "description": "AI 대화 기능",
                "category": "특수"
            },
            {
                "name": "대시보드",
                "icon": "📊",
                "description": "실시간 상태 모니터링",
                "category": "관리"
            },
            {
                "name": "통계",
                "icon": "📈",
                "description": "전송 통계 및 리포트",
                "category": "관리"
            }
        ]

        # 기능 버튼 생성
        self.create_function_buttons()

        # 기본값으로 "기본 전송" 선택
        self.select_function("기본 전송")

    def create_function_buttons(self):
        """기능 버튼들 생성"""
        # 카테고리별 그룹화
        categories = {}
        for func in self.functions:
            category = func["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(func)

        # 카테고리별 버튼 생성
        for category, funcs in categories.items():
            # 카테고리 라벨
            if len(categories) > 1:  # 카테고리가 여러 개인 경우만 표시
                category_label = ctk.CTkLabel(
                    self,
                    text=category,
                    font=("", 11, "bold"),
                    text_color="gray"
                )
                category_label.pack(anchor="w", padx=15, pady=(10, 5))

            # 기능 버튼들
            for func in funcs:
                button = ctk.CTkButton(
                    self,
                    text=f"{func['icon']} {func['name']}",
                    height=45,
                    anchor="w",
                    command=lambda f=func['name']: self.select_function(f)
                )
                button.pack(fill="x", padx=10, pady=2)

                # 툴팁 효과 (마우스 오버 시 설명 표시)
                self.create_tooltip(button, func['description'])

                self.function_buttons[func['name']] = button

    def create_tooltip(self, widget, text):
        """버튼에 툴팁 추가"""
        def show_tooltip(event):
            # 간단한 툴팁 구현 (선택사항)
            pass

        widget.bind("<Enter>", show_tooltip)

    def select_function(self, function_name: str):
        """기능 선택"""
        # 이전 선택 버튼 색상 리셋
        if self.current_function:
            self.function_buttons[self.current_function].configure(
                fg_color=["#3B8ED0", "#1F6AA5"]
            )

        # 현재 선택 버튼 강조
        self.function_buttons[function_name].configure(
            fg_color=self.COLORS["primary"]
        )

        # 상태 업데이트
        self.current_function = function_name
        self.show_info(f"기능 선택: {function_name}")

        # 콜백 실행
        if self.on_function_change:
            self.on_function_change(function_name)

    def set_function_change_callback(self, callback: Callable[[str], None]):
        """기능 변경 콜백 설정"""
        self.on_function_change = callback

    def get_current_function(self) -> Optional[str]:
        """현재 선택된 기능 반환"""
        return self.current_function
