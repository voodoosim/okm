import customtkinter as ctk
from .base_panel import BasePanel
from tkinter import filedialog
import os


class TerminalPanel(BasePanel):
    """통합 터미널 패널 - 하단 영역"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack_propagate(False)  # 고정 높이 유지
        self.command_history = []
        self.history_index = -1
        self.setup_ui()
        print("TerminalPanel initialized")

    def setup_ui(self):
        """터미널 패널 UI 설정"""
        print("Setting up TerminalPanel UI...")
        # 헤더 영역
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        print("Header frame created")

        # 제목
        ctk.CTkLabel(
            header_frame,
            text="통합 터미널",
            font=("", 14, "bold")
        ).pack(side="left")
        print("Title label added")

        # 터미널 옵션 버튼
        options_frame = ctk.CTkFrame(header_frame)
        options_frame.pack(side="right")
        print("Options frame created")

        ctk.CTkButton(
            options_frame,
            text="지우기",
            width=60,
            height=25,
            command=self.clear_terminal
        ).pack(side="right", padx=5)
        print("Clear button added")

        ctk.CTkButton(
            options_frame,
            text="로그 저장",
            width=80,
            height=25,
            command=self.save_terminal_log
        ).pack(side="right", padx=5)
        print("Save log button added")

        # 터미널 출력 영역
        self.terminal_output = ctk.CTkTextbox(
            self,
            state="disabled",
            font=("Consolas", 11),
            wrap="word"
        )
        self.terminal_output.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        print("Terminal output textbox added")

        # 입력 영역
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        print("Input frame created")

        # 프롬프트 라벨
        self.prompt_label = ctk.CTkLabel(
            input_frame,
            text="TelegramCtrl>",
            font=("Consolas", 11, "bold"),
            text_color=self.COLORS["primary"]
        )
        self.prompt_label.pack(side="left", padx=5)
        print("Prompt label added")

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
        self.command_entry.focus_set()  # 포커스 설정
        print("Command entry added and focused")

        # 빠른 액션 버튼들
        actions_frame = ctk.CTkFrame(input_frame)
        actions_frame.pack(side="right", padx=5)
        print("Actions frame created")

        ctk.CTkButton(
            actions_frame,
            text="📎",
            width=30,
            height=30,
            command=self.attach_file
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions_frame,
            text="📷",
            width=30,
            height=30,
            command=self.attach_image
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            actions_frame,
            text="📋",
            width=30,
            height=30,
            command=self.paste_from_clipboard
        ).pack(side="left", padx=2)
        print("Action buttons added")

        # 환영 메시지
        self.print_terminal("=== 텔레그램 멀티컨트롤 터미널 ===")
        self.print_terminal("명령어 목록: help")
        self.print_terminal("")
        print("Welcome message printed")

    def execute_command(self, event=None):
        """명령어 실행"""
        print("Executing command...")
        command = self.command_entry.get().strip()
        if not command:
            print("No command entered")
            return "break"

        # 명령어 히스토리에 추가
        self.command_history.append(command)
        self.history_index = len(self.command_history)

        # 터미널에 명령어 출력
        self.print_terminal(f"TelegramCtrl> {command}")
        print(f"Command executed: {command}")

        # 명령어 처리
        self.process_command(command)

        # 입력 필드 비우기
        self.command_entry.delete(0, "end")
        return "break"

    def process_command(self, command: str):
        """명령어 처리"""
        print(f"Processing command: {command}")
        cmd_parts = command.split()
        if not cmd_parts:
            return

        cmd = cmd_parts[0].lower()
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

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
            selected_sessions = self.parent.get_selected_sessions()
            self.print_terminal(f"선택된 세션: {len(selected_sessions)}개")

            if hasattr(self.parent, 'function_panel'):
                current_function = self.parent.function_panel.get_current_function()
                self.print_terminal(f"현재 기능: {current_function or '없음'}")

            self.print_terminal("애플리케이션 상태: 정상")
        except Exception as e:
            self.print_terminal(f"상태 확인 오류: {str(e)}")

    def show_sessions(self):
        """세션 목록 표시"""
        try:
            selected_sessions = self.parent.get_selected_sessions()
            if selected_sessions:
                self.print_terminal("활성 세션:")
                for session in selected_sessions:
                    self.print_terminal(f"  - {session}")
            else:
                self.print_terminal("선택된 세션이 없습니다.")
        except Exception as e:
            self.print_terminal(f"세션 목록 오류: {str(e)}")

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
        self.print_terminal("세션 연결 테스트 시작...")
        # TODO: Grok의 SessionManager와 연동하여 실제 테스트 구현
        self.print_terminal("구현 예정...")

    def test_message(self):
        """메시지 전송 테스트"""
        self.print_terminal("메시지 전송 테스트 시작...")
        # TODO: 메시지 전송 테스트 구현
        self.print_terminal("구현 예정...")

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

    def print_terminal(self, text: str, color: str = None):
        """터미널에 텍스트 출력"""
        self.terminal_output.configure(state="normal")
        if color:
            pass  # 색상 텍스트 추가 (향후 구현)
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
                self.print_terminal(f"로그 저장 완료: {file_path}")
        except Exception as e:
            self.print_terminal(f"로그 저장 오류: {str(e)}")

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

    def attach_file(self):
        """파일 첨부"""
        try:
            file_path = filedialog.askopenfilename(
                title="파일 선택",
                filetypes=[("모든 파일", "*.*")]
            )
            if file_path:
                file_name = os.path.basename(file_path)
                self.print_terminal(f"파일 첨부: {file_name}")
                # TODO: 파일 첨부 기능 구현
        except Exception as e:
            self.print_terminal(f"파일 첨부 오류: {str(e)}")

    def attach_image(self):
        """이미지 첨부"""
        try:
            file_path = filedialog.askopenfilename(
                title="이미지 선택",
                filetypes=[
                    ("이미지 파일", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("모든 파일", "*.*")
                ]
            )
            if file_path:
                file_name = os.path.basename(file_path)
                self.print_terminal(f"이미지 첨부: {file_name}")
                # TODO: 이미지 첨부 기능 구현
        except Exception as e:
            self.print_terminal(f"이미지 첨부 오류: {str(e)}")

    def paste_from_clipboard(self):
        """클립보드에서 붙여넣기"""
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                current_text = self.command_entry.get()
                self.command_entry.delete(0, "end")
                self.command_entry.insert(0, current_text + clipboard_text)
                self.print_terminal("클립보드 내용 붙여넣기 완료")  # f-string 제거
        except Exception as e:
            self.print_terminal(f"클립보드 오류: {str(e)}")
