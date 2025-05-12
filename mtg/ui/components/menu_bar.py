import customtkinter as ctk

from ..base_window import BaseWindow

class MenuBar(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.create()

    def create(self):
        """메뉴바 생성 (CustomTkinter 방식으로 변경)"""
        # 기존 tkinter 메뉴 제거
        self.root.configure(menu=None)

        # 메뉴 프레임 생성
        menu_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        menu_frame.pack(fill="x", side="top")

        # 파일 메뉴 버튼
        file_button = ctk.CTkButton(
            menu_frame,
            text="파일",
            width=60,
            height=30,
            command=self.show_file_menu,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        file_button.pack(side="left", padx=5)

        # 도움말 메뉴 버튼
        help_button = ctk.CTkButton(
            menu_frame,
            text="도움말",
            width=60,
            height=30,
            command=self.show_help_menu,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        help_button.pack(side="left", padx=5)

    def show_file_menu(self):
        """파일 메뉴 표시"""
        menu = ctk.CTkToplevel()
        menu.title("")
        menu.geometry("100x70+100+30")
        menu.resizable(False, False)
        menu.attributes('-topmost', True)

        settings_btn = ctk.CTkButton(menu, text="설정", command=lambda: [menu.destroy(), self.parent.open_settings()])
        settings_btn.pack(pady=5)

        exit_btn = ctk.CTkButton(menu, text="종료", command=lambda: [menu.destroy(), self.parent.quit()])
        exit_btn.pack(pady=5)

    def show_help_menu(self):
        """도움말 메뉴 표시"""
        menu = ctk.CTkToplevel()
        menu.title("")
        menu.geometry("100x70+200+30")
        menu.resizable(False, False)
        menu.attributes('-topmost', True)

        help_btn = ctk.CTkButton(menu, text="사용법", command=lambda: [menu.destroy(), self.parent.show_help()])
        help_btn.pack(pady=5)

        about_btn = ctk.CTkButton(menu, text="정보", command=lambda: [menu.destroy(), self.parent.show_about()])
        about_btn.pack(pady=5)
