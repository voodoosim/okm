import asyncio
import threading
import os

import customtkinter as ctk
import tkinter.ttk as ttk  # 추가
from tkinter import messagebox

from ..base_window import BaseWindow

class SessionTab(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.session_tree = None
        self.tab = None
        self.create()

    def create(self):
        """세션 관리 탭 생성"""
        self.tab = self.parent.tabview.tab("세션 관리")

        button_frame = ctk.CTkFrame(self.tab, corner_radius=8)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(button_frame, text="새 세션 생성", command=self.parent.create_new_session).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="세션 새로고침", command=self.refresh_sessions).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="세션 삭제", command=self.delete_session).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Unknown 계정 삭제", command=self.delete_unknown_sessions).pack(side="left", padx=5)

        columns = ("이름", "사용자명", "전화번호", "상태")
        self.session_tree = ttk.Treeview(self.tab, columns=columns, show="headings")  # 수정

        for col in columns:
            self.session_tree.heading(col, text=col)
            self.session_tree.column(col, width=150)

        self.session_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_sessions()

    def refresh_sessions(self):
        """세션 목록 새로고침"""
        if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
            self.parent.log_panel.append_log("세션 새로고침 시작")
        else:
            print("세션 새로고침 시작")

        for item in self.session_tree.get_children():
            self.session_tree.delete(item)

        # 비동기 작업을 별도 스레드로 실행
        thread = threading.Thread(target=self._load_sessions_threaded)
        thread.start()

    def _load_sessions_threaded(self):
        """스레드에서 비동기 세션 로드"""
        async def load():
            try:
                if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
                    self.parent.log_panel.append_log("세션 로드 중...")
                else:
                    print("세션 로드 중...")

                sessions = await self.session_manager.load_sessions()

                if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
                    self.parent.log_panel.append_log(f"세션 로드 완료: {len(sessions)}개 세션")
                else:
                    print(f"세션 로드 완료: {len(sessions)}개 세션")

                self.root.after(0, self._update_session_tree, sessions)
            except Exception as e:
                if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
                    self.parent.log_panel.append_log(f"세션 로드 중 오류 발생: {str(e)}")
                else:
                    print(f"세션 로드 중 오류 발생: {str(e)}")
                self.root.after(0, messagebox.showerror, "오류", f"세션 로드 중 오류 발생: {str(e)}")

        # 새로운 이벤트 루프 생성
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(load())
        new_loop.close()

    def _update_session_tree(self, sessions):
        """세션 트리뷰 업데이트"""
        if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
            self.parent.log_panel.append_log("세션 트리뷰 업데이트 시작")
        else:
            print("세션 트리뷰 업데이트 시작")

        for session in sessions:
            status = session["status"]
            item = self.session_tree.insert("", "end", values=(
                session["name"],
                session["username"],
                f"...{session['phone']}",
                status
            ))
            self.session_tree.tag_configure(status, background=self.parent.STATUS_COLORS.get(status, '#CCCCCC'))
            self.session_tree.item(item, tags=(status,))

        if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
            self.parent.log_panel.append_log("세션 트리뷰 업데이트 완료")
        else:
            print("세션 트리뷰 업데이트 완료")

    def delete_session(self):
        """선택된 세션 삭제"""
        selected_items = self.session_tree.selection()
        if not selected_items:
            messagebox.showwarning("경고", "삭제할 세션을 선택하세요.")
            return

        for item in selected_items:
            session_name = self.session_tree.item(item)["values"][0]
            session_path = os.path.join(self.parent.config["app_settings"]["session_dir"], f"{session_name}.session")
            if os.path.exists(session_path):
                os.remove(session_path)
                self.event_logger.on_error_occurred({"event": "session_deleted", "session_name": session_name})
                if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
                    self.parent.log_panel.append_log(f"세션 삭제됨: {session_name}")
                else:
                    print(f"세션 삭제됨: {session_name}")

        self.refresh_sessions()

    def delete_unknown_sessions(self):
        """Unknown 상태 세션 일괄 삭제"""
        for item in self.session_tree.get_children():
            values = self.session_tree.item(item)["values"]
            if values[3] == "unknown":
                session_name = values[0]
                session_path = os.path.join(self.parent.config["app_settings"]["session_dir"], f"{session_name}.session")
                if os.path.exists(session_path):
                    os.remove(session_path)
                    self.event_logger.on_error_occurred({"event": "session_deleted", "session_name": session_name})
                    if hasattr(self.parent, 'log_panel') and self.parent.log_panel:
                        self.parent.log_panel.append_log(f"Unknown 세션 삭제됨: {session_name}")
                    else:
                        print(f"Unknown 세션 삭제됨: {session_name}")

        self.refresh_sessions()

    def get_session_tree(self):
        """session_tree 속성 반환"""
        return self.session_tree
