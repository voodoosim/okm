import asyncio
import tkinter as tk

import customtkinter as ctk
from tkinter import messagebox

from ..base_window import BaseWindow

class SettingsDialog(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.top = ctk.CTkToplevel(self.root)
        self.top.title("설정")
        self.top.geometry("600x500")

        self.config_manager = self.parent.config_manager
        self.rate_limiter = self.parent.rate_limiter
        self.message_sender = self.parent.message_sender
        self.config = self.config_manager.config.copy()

        self.api_id_entry = None
        self.api_hash_entry = None
        self.daily_limit_var = None
        self.hourly_limit_var = None
        self.personal_min_var = None
        self.personal_max_var = None
        self.group_min_var = None
        self.group_max_var = None
        self.concurrent_var = None
        self.priority_var = None

        self.create()

    def create(self):
        tabview = ctk.CTkTabview(self.top, corner_radius=10)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        tabview.add("API 설정")
        tabview.add("제한 설정")

        self.create_api_tab(tabview.tab("API 설정"))
        self.create_limits_tab(tabview.tab("제한 설정"))

        button_frame = ctk.CTkFrame(self.top)
        button_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        ctk.CTkButton(button_frame, text="저장", command=self.save_settings).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="취소", command=self.top.destroy).pack(side="right", padx=5)

    def create_api_tab(self, parent):
        """API 설정 탭 생성"""
        ctk.CTkLabel(parent, text="API ID:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_id_entry = ctk.CTkEntry(parent, width=400)
        self.api_id_entry.grid(row=0, column=1, padx=10, pady=10)
        self.api_id_entry.insert(0, str(self.config["api_settings"]["api_id"] or ""))

        ctk.CTkLabel(parent, text="API Hash:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.api_hash_entry = ctk.CTkEntry(parent, width=400)
        self.api_hash_entry.grid(row=1, column=1, padx=10, pady=10)
        self.api_hash_entry.insert(0, self.config["api_settings"]["api_hash"] or "")

    def create_limits_tab(self, parent):
        """제한 설정 탭 생성"""
        ctk.CTkLabel(parent, text="일일 계정당 제한:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.daily_limit_var = tk.StringVar(value=str(self.config["rate_limits"]["daily_per_account"]))
        ctk.CTkEntry(parent, textvariable=self.daily_limit_var, width=100).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="시간당 계정당 제한:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.hourly_limit_var = tk.StringVar(value=str(self.config["rate_limits"]["hourly_per_account"]))
        ctk.CTkEntry(parent, textvariable=self.hourly_limit_var, width=100).grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="개인 채팅 최소 지연(초):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.personal_min_var = tk.StringVar(value=str(self.config["rate_limits"]["personal_min_delay"]))
        ctk.CTkEntry(parent, textvariable=self.personal_min_var, width=100).grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="개인 채팅 최대 지연(초):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.personal_max_var = tk.StringVar(value=str(self.config["rate_limits"]["personal_max_delay"]))
        ctk.CTkEntry(parent, textvariable=self.personal_max_var, width=100).grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="그룹 채팅 최소 지연(초):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.group_min_var = tk.StringVar(value=str(self.config["rate_limits"]["group_min_delay"]))
        ctk.CTkEntry(parent, textvariable=self.group_min_var, width=100).grid(row=4, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="그룹 채팅 최대 지연(초):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.group_max_var = tk.StringVar(value=str(self.config["rate_limits"]["group_max_delay"]))
        ctk.CTkEntry(parent, textvariable=self.group_max_var, width=100).grid(row=5, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="최대 동시 전송 계정:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.concurrent_var = tk.StringVar(value=str(self.config["rate_limits"]["max_concurrent_accounts"]))
        ctk.CTkEntry(parent, textvariable=self.concurrent_var, width=100).grid(row=6, column=1, padx=10, pady=5)

        ctk.CTkLabel(parent, text="계정 선택 우선순위:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.priority_var = tk.StringVar(value=self.config["rate_limits"]["priority_mode"])
        priority_combo = ctk.CTkComboBox(parent, variable=self.priority_var, values=["balanced", "sequential", "round_robin", "least_used"], width=150)
        priority_combo.grid(row=7, column=1, padx=10, pady=5)

    def save_settings(self):
        """설정 저장"""
        try:
            self.config["api_settings"]["api_id"] = int(self.api_id_entry.get()) if self.api_id_entry.get() else None
            self.config["api_settings"]["api_hash"] = self.api_hash_entry.get() if self.api_hash_entry.get() else None

            self.config["rate_limits"]["daily_per_account"] = int(self.daily_limit_var.get())
            self.config["rate_limits"]["hourly_per_account"] = int(self.hourly_limit_var.get())
            self.config["rate_limits"]["personal_min_delay"] = float(self.personal_min_var.get())
            self.config["rate_limits"]["personal_max_delay"] = float(self.personal_max_var.get())
            self.config["rate_limits"]["group_min_delay"] = float(self.group_min_var.get())
            self.config["rate_limits"]["group_max_delay"] = float(self.group_max_var.get())
            self.config["rate_limits"]["max_concurrent_accounts"] = int(self.concurrent_var.get())
            self.config["rate_limits"]["priority_mode"] = self.priority_var.get()

            self.config = self.config_manager.validate_config(self.config)
            self.config_manager.save_config(self.config)

            self.rate_limiter.__init__(
                self.config["rate_limits"]["daily_per_account"],
                self.config["rate_limits"]["hourly_per_account"],
                self.config["rate_limits"]["personal_min_delay"],
                self.config["rate_limits"]["personal_max_delay"],
                self.config["rate_limits"]["group_min_delay"],
                self.config["rate_limits"]["group_max_delay"],
                self.config["rate_limits"]["flood_wait_buffer"]
            )
            self.rate_limiter.config = self.config
            self.message_sender.semaphore = asyncio.Semaphore(self.config["rate_limits"]["max_concurrent_accounts"])

            messagebox.showinfo("완료", "설정이 저장되었습니다.")
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("오류", f"잘못된 입력값입니다: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류: {str(e)}")
