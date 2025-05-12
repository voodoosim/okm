import customtkinter as ctk

from ...base_window import BaseWindow
from .mode_manager import ModeManager

class ConversationModesTab(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.tab = None
        self.mode_tabview = None
        self.mode_manager = ModeManager(self)
        self.active_modes = {}
        self.create()

    def create(self):
        """대화 모드 탭 생성"""
        self.tab = self.parent.tabview.tab("대화 모드")

        # 모드 선택 UI
        selection_frame = ctk.CTkFrame(self.tab, corner_radius=10)
        selection_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(selection_frame, text="모드 선택:", font=("", 14, "bold")).pack(side="left", padx=10)
        self.mode_var = ctk.StringVar(value="없음")
        mode_menu = ctk.CTkOptionMenu(selection_frame, values=["없음"] + list(self.mode_manager.available_modes.keys()), variable=self.mode_var)
        mode_menu.pack(side="left", padx=10)

        ctk.CTkButton(selection_frame, text="모드 추가", command=self.add_mode).pack(side="left", padx=10)
        ctk.CTkButton(selection_frame, text="모드 제거", command=self.remove_mode).pack(side="left", padx=5)

        # 탭 뷰
        self.mode_tabview = ctk.CTkTabview(self.tab, corner_radius=10)
        self.mode_tabview.pack(fill="both", expand=True, padx=10, pady=10)

    def add_mode(self):
        """선택된 모드를 탭으로 추가"""
        mode_name = self.mode_var.get()
        if mode_name == "없음":
            return

        # 더 안전한 None 체크
        tab_names = []
        if hasattr(self.mode_tabview, '_tab_dict') and self.mode_tabview._tab_dict is not None:
            tab_names = list(self.mode_tabview._tab_dict.keys())

        if mode_name not in tab_names:
            self.mode_manager.create_tab(self.mode_tabview, mode_name)
            self.mode_tabview.set(mode_name)
            mode_instance = self.mode_manager.load_mode(mode_name)
            if mode_instance:
                self.active_modes[mode_name] = mode_instance[0]
        else:
            self.mode_tabview.set(mode_name)

    def remove_mode(self):
        """현재 활성 모드 제거"""
        current_tab = self.mode_tabview.get()
        if current_tab and current_tab != "없음":
            self.mode_tabview.delete(current_tab)
            if current_tab in self.active_modes:
                del self.active_modes[current_tab]

    def get_selected_accounts(self):
        """선택된 계정 리스트 반환 (모드에서 사용)"""
        if hasattr(self.parent, 'session_tab'):
            return self.parent.session_tab.get_selected_accounts()
        return []

    def get_current_mode(self):
        """현재 활성화된 모드 반환"""
        current_tab = self.mode_tabview.get()
        return self.active_modes.get(current_tab)
