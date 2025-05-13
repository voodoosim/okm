import customtkinter as ctk
import threading
from .base_panel import BasePanel
from typing import List, Dict


class SessionPanel(BasePanel):
    """세션 관리 패널"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)  # 고정 너비 유지
        self.session_checkboxes = {}
        self.session_data = []
        self.session_manager = None
        self.setup_ui()
        print("SessionPanel initialized")

    def setup_ui(self):
        """세션 패널 UI 설정"""
        print("Setting up SessionPanel UI...")
        # 헤더 영역
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        print("Header frame created")

        # 제목
        ctk.CTkLabel(
            header_frame,
            text="계정 선택",
            font=("", 14, "bold")
        ).pack(side="left")
        print("Title label added")

        # 선택 카운터
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="0개 선택",
            text_color="gray"
        )
        self.count_label.pack(side="right")
        print("Count label added")

        # 컨트롤 버튼 영역
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=(0, 5))
        print("Control frame created")

        # 새 세션 버튼
        ctk.CTkButton(
            control_frame,
            text="새 세션",
            height=30,
            command=self.show_create_session_dialog  # 다이얼로그 메서드 연결
        ).pack(side="left", fill="x", expand=True, padx=(0, 2))
        print("New session button added")

        # 새로고침 버튼
        ctk.CTkButton(
            control_frame,
            text="새로고침",
            height=30,
            command=self.refresh_sessions
        ).pack(side="right", fill="x", expand=True, padx=(2, 0))
        print("Refresh button added")

        # 전체 선택 체크박스
        self.select_all_var = ctk.BooleanVar()
        self.select_all_checkbox = ctk.CTkCheckBox(
            self,
            text="전체 선택",
            variable=self.select_all_var,
            command=self.toggle_all_sessions
        )
        self.select_all_checkbox.pack(anchor="w", padx=10, pady=5)
        print("Select all checkbox added")

        # 세션 목록 스크롤 영역
        self.session_scrollframe = ctk.CTkScrollableFrame(self)
        self.session_scrollframe.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        print("Session scroll frame added")

        # 상태 라벨
        self.status_label = ctk.CTkLabel(
            self.session_scrollframe,
            text="세션 로딩 중...",
            text_color="gray"
        )
        self.status_label.pack(pady=20)
        print("Status label added")

    def set_session_manager(self, session_manager):
        """세션 매니저 설정"""
        self.session_manager = session_manager
        self.refresh_sessions()

    def refresh_sessions(self):
        """세션 목록 새로고침"""
        if not self.session_manager:
            self.show_error("SessionManager가 설정되지 않았습니다.")
            return

        self.show_info("세션 목록 새로고침 중...")
        self.clear_session_display()

        # 비동기 로드
        threading.Thread(target=self._load_sessions_async, daemon=True).start()

    def _load_sessions_async(self):
        """비동기로 세션 데이터 로드"""
        try:
            sessions = self.session_manager.get_session_list()
            self.after(0, self._update_session_display, sessions)
        except Exception as e:
            self.after(0, self.show_error, f"세션 로드 오류: {str(e)}")

    def clear_session_display(self):
        """세션 디스플레이 정리"""
        for widget in self.session_scrollframe.winfo_children():
            widget.destroy()
        self.session_checkboxes.clear()
        self.session_data.clear()
        self.update_count()

    def _update_session_display(self, sessions: List[Dict[str, str]]):
        """세션 목록 디스플레이 업데이트"""
        if not sessions:
            no_sessions_label = ctk.CTkLabel(
                self.session_scrollframe,
                text="세션이 없습니다.",
                text_color="gray"
            )
            no_sessions_label.pack(pady=20)
            return

        self.session_data = sessions

        for session in sessions:
            session_frame = ctk.CTkFrame(self.session_scrollframe, corner_radius=6)
            session_frame.pack(fill="x", padx=2, pady=1)

            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                session_frame,
                text="",
                variable=var,
                width=20,
                command=self.update_count
            )
            checkbox.pack(side="left", padx=8, pady=8)

            info_frame = ctk.CTkFrame(session_frame, corner_radius=0)
            info_frame.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=4)

            primary_text = session['name']
            if session['username'] != 'Unknown' and session['username'] != f"...{session['name']}":
                primary_text += f" ({session['username']})"

            name_label = ctk.CTkLabel(
                info_frame,
                text=primary_text,
                font=("", 12, "bold"),
                anchor="w"
            )
            name_label.pack(fill="x", pady=(2, 0))

            status_color = self._get_status_color(session['status'])
            secondary_text = f"{session['phone']} • {session['status'].upper()}"

            status_label = ctk.CTkLabel(
                info_frame,
                text=secondary_text,
                font=("", 10),
                text_color=status_color,
                anchor="w"
            )
            status_label.pack(fill="x", pady=(0, 2))

            self.session_checkboxes[session['name']] = var

        self.show_info(f"세션 로드 완료: {len(sessions)}개")
        self.update_count()

    def _get_status_color(self, status: str) -> str:
        """상태별 색상 반환"""
        color_map = {
            "active": self.COLORS["success"],
            "inactive": self.COLORS["warning"],
            "unknown": self.COLORS["error"]
        }
        return color_map.get(status, "#FFFFFF")

    def toggle_all_sessions(self):
        """전체 세션 선택/해제"""
        select_all = self.select_all_var.get()
        for var in self.session_checkboxes.values():
            var.set(select_all)
        self.update_count()

    def update_count(self):
        """선택된 세션 수 업데이트"""
        selected = len(self.get_selected_sessions())
        total = len(self.session_checkboxes)
        self.count_label.configure(text=f"{selected}/{total}개 선택")

    def get_selected_sessions(self) -> List[str]:
        """선택된 세션 이름 목록 반환"""
        selected = []
        for session_name, var in self.session_checkboxes.items():
            if var.get():
                selected.append(session_name)
        return selected

    def show_create_session_dialog(self):
        """새 세션 생성 다이얼로그 표시"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("새 세션 생성")
        dialog.geometry("350x180")
        dialog.transient(self.parent)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="새 텔레그램 세션 생성", font=("", 16, "bold")).pack(pady=15)
        ctk.CTkLabel(dialog, text="전화번호:").pack()
        phone_entry = ctk.CTkEntry(dialog, placeholder_text="+821234567890", width=250)
        phone_entry.pack(pady=10)
        phone_entry.focus()

        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=15)

        def create_session():
            phone = phone_entry.get().strip()
            if not phone:
                self.show_error("전화번호를 입력해주세요.")
                return
            result = self.parent.create_new_session(phone)
            dialog.destroy()
            if result["success"]:
                self.show_info(f"새 세션 생성: {phone}")
            else:
                self.show_error(f"세션 생성 실패: {result['error']}")

        ctk.CTkButton(btn_frame, text="생성", command=create_session).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="취소", command=dialog.destroy).pack(side="right")
