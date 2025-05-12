import customtkinter as ctk
import tkinter.ttk as ttk  # 추가

from ..base_window import BaseWindow

class DashboardTab(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.active_accounts_label = None
        self.current_rate_label = None
        self.accounts_tree = None
        self.tab = None
        self.create()

    def create(self):
        """대시보드 탭 생성"""
        self.tab = self.parent.tabview.tab("대시보드")

        status_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=10)

        self.active_accounts_label = ctk.CTkLabel(status_frame, text="활성 계정: 0/0")
        self.active_accounts_label.pack(anchor="w", padx=10, pady=2)

        self.current_rate_label = ctk.CTkLabel(status_frame, text="현재 전송률: 0 메시지/분")
        self.current_rate_label.pack(anchor="w", padx=10, pady=2)

        accounts_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        accounts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("계정", "상태", "일일 남음", "시간당 남음", "분당 남음")
        self.accounts_tree = ttk.Treeview(accounts_frame, columns=columns, show="headings")  # 수정

        for col in columns:
            self.accounts_tree.heading(col, text=col)
            self.accounts_tree.column(col, width=120)

        self.accounts_tree.pack(fill="both", expand=True)

    def get_active_accounts_label(self):
        """active_accounts_label 속성 반환"""
        return self.active_accounts_label

    def get_current_rate_label(self):
        """current_rate_label 속성 반환"""
        return self.current_rate_label

    def get_accounts_tree(self):
        """accounts_tree 속성 반환"""
        return self.accounts_tree
