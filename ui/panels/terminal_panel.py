# ui/panels/terminal_panel.py 전체 수정
import customtkinter as ctk
from .base_panel import BasePanel
from tkinter import filedialog
import os
from typing import Optional
import threading
import time

class TerminalPanel(BasePanel):
    """통합 터미널 패널 - 하단 영역"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)  # 고정 높이 유지
        self.command_history = []
        self.history_index = -1
        self.session_manager = None
        self.message_sender = None
        self.setup_ui()

    def setup_ui(self):
        """터미널 패널 UI 설정"""
        # 헤더 영역
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        # 제목
        ctk.CTkLabel(
            header_frame,
            text="통합 터미널",
            font=("", 14, "bold")
        ).pack(side="left")

        # 터미널 옵션 버튼
        options_frame = ctk.CTkFrame(header_frame)
        options_frame.pack(side="right")

        ctk.CTkButton(
            options_frame,
            text="지우기",
            width=60,
            height=25,
            command=self.clear_terminal
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            options_frame,
            text="로그 저장",
            width=80,
            height=25,
            command=self.save_terminal_log
        ).pack(side="right", padx=5)

        # 터미널 출력 영역
        self.terminal_output = ctk.CTkTextbox(
            self,
            state="disabled",
            font=("Consolas", 11),
            wrap="word"
        )
        self.terminal_output.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # 입력 영역
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 프롬프트 라벨
        self.prompt_label = ctk.CTkLabel(
            input_frame,
            text="TelegramCtrl>",
            font=("Consolas", 11, "bold"),
            text_color=self.COLORS["primary"]
        )
        self.prompt_label.pack(side="left", padx=5)

        # 명령 입력
        self.command_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="명령 입력... (help for commands)",
            font=("Consolas", 11)
        )
        self.command_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.bind("<Up>", self.previous_command)
        self.command_entry.bind("<Down>", self.next_command)

        # 환영 메시지
        self.print_terminal("=== 텔레그램 멀티컨트롤 터미널 ===")
        self.print_terminal("명령어 목록: help")
        self.print_terminal("")

    def set_session_manager(self, session_manager):
        """세션 매니저 설정"""
        self.session_manager = session_manager
        self.print_terminal("SessionManager 연결 완료", 'cyan')

    def set_message_sender(self, message_sender):
        """메시지 센더 설정"""
        self.message_sender = message_sender
        if message_sender:
            self.print_terminal("MessageSender 연결 완료", 'cyan')

    def execute_command(self, event=None):
        """명령어 실행"""
        command = self.command_entry.get().strip()
        if not command:
            return "break"

        # 명령어 히스토리에 추가
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # 터미널에 명령어 출력
        self.print_terminal(f"TelegramCtrl> {command}")

        # 명령어 처리
        self.process_command(command)

        # 입력 필드 비우기
        self.command_entry.delete(0, "end")
        return "break"

    def process_command(self, command: str):
        """명령어 처리"""
        cmd_parts = command.split()
        if not cmd_parts:
            return

        cmd = cmd_parts[0].lower()
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

        # 내장 명령어 처리
        if cmd == "help":
            self.show_help()
        elif cmd == "clear":
            self.clear_terminal()
        elif cmd == "status":
            self.show_status()
        elif cmd == "sessions":
            self.show_sessions()
        elif cmd == "test":
            self.run_test(args)
        elif cmd == "log":
            self.show_log_commands()
        elif cmd == "echo":
            self.print_terminal(" ".join(args))
        elif cmd == "exit" or cmd == "quit":
            self.print_terminal("터미널을 종료할 수 없습니다.")
        else:
            self.print_terminal(f"알 수 없는 명령어: {cmd}")
            self.print_terminal("사용 가능한 명령어는 'help'를 입력하세요.")

    def show_help(self):
        """도움말 표시"""
        help_text = """
사용 가능한 명령어:

기본 명령어:
  help         - 이 도움말을 표시
  clear        - 터미널 화면 지우기
  status       - 현재 상태 확인
  sessions     - 활성 세션 목록 표시
  log          - 로그 관련 명령어

테스트 명령어:
  test session - 세션 연결 테스트
  test message - 메시지 전송 테스트

기타:
  echo <text>  - 텍스트 출력

단축키:
  Enter        - 명령어 실행
  ↑/↓ 키      - 명령어 히스토리 탐색
  Ctrl+C       - 현재 작업 중단 (구현 예정)
"""
        self.print_terminal(help_text)

    def show_status(self):
        """현재 상태 표시"""
        try:
            # 세션 상태
            selected_sessions = self.parent.get_selected_sessions()
            self.print_terminal(f"선택된 세션: {len(selected_sessions)}개")

            # 현재 기능
            if hasattr(self.parent, 'function_panel'):
                current_function = self.parent.function_panel.get_current_function()
                self.print_terminal(f"현재 기능: {current_function or '없음'}")

            # SessionManager 상태
            if self.session_manager:
                self.print_terminal("SessionManager: 연결됨")
            else:
                self.print_terminal("SessionManager: 연결되지 않음", 'red')

            # MessageSender 상태
            if self.message_sender:
                self.print_terminal("MessageSender: 연결됨")
            else:
                self.print_terminal("MessageSender: 연결되지 않음", 'yellow')

            # 애플리케이션 상태
            self.print_terminal("애플리케이션 상태: 정상")

        except Exception as e:
            self.print_terminal(f"상태 확인 오류: {str(e)}", 'red')

    def show_sessions(self):
        """세션 목록 표시"""
        if not self.session_manager:
            self.print_terminal("SessionManager가 연결되지 않았습니다.", 'red')
            return

        try:
            sessions = self.session_manager.get_session_list()
            if sessions:
                self.print_terminal(f"\n활성 세션 목록 ({len(sessions)}개):")
                self.print_terminal("-" * 50)
                for session in sessions:
                    status_icon = {"active": "🟢", "inactive": "🟡", "unknown": "🔴"}.get(session['status'], "❓")
                    self.print_terminal(f"{status_icon} {session['name']} ({session['username']}) - {session['status']}")
            else:
                self.print_terminal("세션이 없습니다.", 'yellow')
        except Exception as e:
            self.print_terminal(f"세션 목록 오류: {str(e)}", 'red')

    def run_test(self, args):
        """테스트 명령어 실행"""
        if not args:
            self.print_terminal("테스트 타입을 지정해주세요. 예: test session")
            return

        test_type = args[0].lower()

        if test_type == "session":
            self.test_sessions()
        elif test_type == "message":
            self.test_message()
        else:
            self.print_terminal(f"알 수 없는 테스트 타입: {test_type}")

    def test_sessions(self):
        """세션 연결 테스트"""
        if not self.session_manager:
            self.print_terminal("SessionManager가 연결되지 않았습니다.", 'red')
            return

        self.print_terminal("세션 연결 테스트 시작...", 'yellow')
        threading.Thread(target=self._test_sessions_async, daemon=True).start()

    def _test_sessions_async(self):
        """비동기 세션 테스트"""
        try:
            sessions = self.session_manager.get_session_list()
            self.after(0, self.print_terminal, f"세션 목록 조회 성공: {len(sessions)}개")

            for session in sessions:
                status = self.session_manager.check_session_status(session['name'])
                status_color = 'green' if status == 'active' else 'yellow' if status == 'inactive' else 'red'
                self.after(0, self.print_terminal, f"  - {session['name']}: {status}", status_color)
                time.sleep(0.1)

            self.after(0, self.print_terminal, "세션 테스트 완료!", 'cyan')
        except Exception as e:
            self.after(0, self.print_terminal, f"세션 테스트 오류: {str(e)}", 'red')

    def test_message(self):
        """메시지 전송 테스트"""
        self.print_terminal("메시지 전송 테스트 시작...", 'yellow')
        if not self.message_sender:
            self.print_terminal("MessageSender가 연결되지 않았습니다.", 'red')
            self.print_terminal("시뮬레이션 모드로 실행합니다.", 'yellow')

            # 시뮬레이션
            for i in range(3):
                time.sleep(0.5)
                self.print_terminal(f"  테스트 단계 {i+1}/3 실행 중...")
            self.print_terminal("메시지 전송 시뮬레이션 완료!", 'cyan')
            return

        # 실제 구현은 MessageSender와 연동
        self.print_terminal("메시지 전송 기능은 개발 중입니다.", 'yellow')

    def show_log_commands(self):
        """로그 관련 명령어 표시"""
        log_help = """
로그 관련 명령어:
  log show     - 최근 로그 표시
  log clear    - 로그 지우기
  log level    - 로그 레벨 설정
  log save     - 로그 파일로 저장
"""
        self.print_terminal(log_help)

    def print_terminal(self, text: str, color: Optional[str] = None):
        """터미널에 텍스트 출력"""
        self.terminal_output.configure(state="normal")

        if color:
            # 색상 태그 설정
            self.terminal_output.tag_config(color, foreground=self.COLORS.get(color, color))
            self.terminal_output.insert("end", text + "\n", color)
        else:
            self.terminal_output.insert("end", text + "\n")

        self.terminal_output.see("end")
        self.terminal_output.configure(state="disabled")

    def clear_terminal(self):
        """터미널 화면 지우기"""
        self.terminal_output.configure(state="normal")
        self.terminal_output.delete("1.0", "end")
        self.terminal_output.configure(state="disabled")
        self.print_terminal("터미널이 지워졌습니다.")

    def save_terminal_log(self):
        """터미널 로그 저장"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
                title="터미널 로그 저장"
            )

            if file_path:
                content = self.terminal_output.get("1.0", "end")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.print_terminal(f"로그 저장 완료: {file_path}", 'cyan')
        except Exception as e:
            self.print_terminal(f"로그 저장 오류: {str(e)}", 'red')

    def previous_command(self, event):
        """이전 명령어 (↑ 키)"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            command = self.command_history[self.history_index]
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, command)
        return "break"

    def next_command(self, event):
        """다음 명령어 (↓ 키)"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            command = self.command_history[self.history_index]
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, command)
        elif self.history_index == len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, "end")
        return "break"
