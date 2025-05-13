import os
from typing import List, Dict, Union
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError
from core.config_manager import ConfigManager

class SessionManager:
    def __init__(self):
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()  # get_config() 메서드 사용

    def get_session_list(self) -> List[Dict[str, str]]:
        """Returns list of sessions with metadata."""
        sessions = []
        for session_file in os.listdir(self.sessions_dir):
            if session_file.endswith(".session"):
                name = session_file.replace(".session", "")
                status = self.check_session_status(name)
                phone = f"...{name[-4:]}"  # Partial phone number
                username = "Unknown"
                try:
                    # config에서 API 정보 가져오기
                    api_id = self.config["api_settings"]["api_id"]
                    api_hash = self.config["api_settings"]["api_hash"]

                    if api_id and api_hash:
                        with TelegramClient(
                            os.path.join(self.sessions_dir, name),
                            api_id,
                            api_hash,
                        ) as client:
                            if client.is_connected():
                                me = client.get_me()
                                username = me.username or "Unknown"
                except Exception:
                    pass
                sessions.append({"name": name, "username": username, "phone": phone, "status": status})
        return sessions

    def check_session_status(self, session_name: str) -> str:
        """Checks session file validity and connection status."""
        session_path = os.path.join(self.sessions_dir, f"{session_name}.session")
        if not os.path.exists(session_path):
            return "unknown"
        try:
            api_id = self.config["api_settings"]["api_id"]
            api_hash = self.config["api_settings"]["api_hash"]

            if not api_id or not api_hash:
                return "unknown"

            with TelegramClient(
                session_path, api_id, api_hash
            ) as client:
                if client.is_connected():
                    return "active"
                return "inactive"
        except Exception:
            return "unknown"

    def create_new_session(self, phone_number: str) -> Dict[str, Union[bool, str]]:
        """Creates new Telegram session."""
        try:
            api_id = self.config["api_settings"]["api_id"]
            api_hash = self.config["api_settings"]["api_hash"]

            if not api_id or not api_hash:
                return {"success": False, "session_name": "", "error": "API ID/Hash not configured"}

            session_name = phone_number.replace("+", "")
            client = TelegramClient(
                os.path.join(self.sessions_dir, session_name),
                api_id,
                api_hash,
            )
            client.start(phone=phone_number)
            return {"success": True, "session_name": session_name, "error": ""}
        except PhoneNumberInvalidError:
            return {"success": False, "session_name": "", "error": "Invalid phone number"}
        except SessionPasswordNeededError:
            return {"success": False, "session_name": "", "error": "2FA required"}
        except Exception as e:
            return {"success": False, "session_name": "", "error": str(e)}
