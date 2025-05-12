import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..base_window import BaseWindow

class StatsTab(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.daily_stats_text = None
        self.tab = None
        self.create()

    def create(self):
        """통계 탭 생성"""
        self.tab = self.parent.tabview.tab("통계")

        daily_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        daily_frame.pack(fill="x", padx=10, pady=10)

        self.daily_stats_text = ctk.CTkTextbox(daily_frame, height=200, state="disabled")
        self.daily_stats_text.pack(fill="both", expand=True)

        button_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(button_frame, text="통계 업데이트", command=self.update_stats).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="리포트 생성", command=self.generate_report).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="로그 폴더 열기", command=self.open_log_folder).pack(side="left", padx=5)

        self.update_stats()

    def update_stats(self):
        """통계 업데이트"""
        stats = self.monitor.get_stats()
        self.daily_stats_text.configure(state="normal")
        self.daily_stats_text.delete("1.0", "end")
        self.daily_stats_text.insert("end", f"총 전송 시도: {stats['total']}회\n")
        self.daily_stats_text.insert("end", f"성공: {stats['success']}회\n")
        self.daily_stats_text.insert("end", f"실패: {stats['failure']}회\n")
        self.daily_stats_text.insert("end", "\n계정별 통계:\n")
        for account, acc_stats in stats["accounts"].items():
            self.daily_stats_text.insert("end", f"- {account}: 성공 {acc_stats['success']}, 실패 {acc_stats['failure']}\n")
        self.daily_stats_text.configure(state="disabled")

    def generate_report(self):
        """리포트 생성"""
        self.monitor.generate_daily_report()
        messagebox.showinfo("성공", "일일 리포트가 생성되었습니다.")
        if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
            self.parent.log_panel.append_log("일일 리포트 생성됨")
        else:
            print("일일 리포트 생성됨")

    def open_log_folder(self):
        """로그 폴더 열기"""
        log_dir = self.parent.config["app_settings"]["log_dir"]
        filedialog.askdirectory(initialdir=log_dir, title="로그 폴더 열기")
        if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
            self.parent.log_panel.append_log("로그 폴더 열림")
        else:
            print("로그 폴더 열림")
