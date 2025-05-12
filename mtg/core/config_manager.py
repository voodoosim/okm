import json
import os
import subprocess

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """config.json에서 설정 로드"""
        default_config = {
            "api_settings": {
                "api_id": None,
                "api_hash": None
            },
            "rate_limits": {
                "daily_per_account": 500,
                "hourly_per_account": 100,
                "personal_min_delay": 1.5,
                "personal_max_delay": 3,
                "group_min_delay": 3,
                "group_max_delay": 6,
                "flood_wait_buffer": 60,
                "priority_mode": "balanced",
                "max_concurrent_accounts": 5
            },
            "app_settings": {
                "session_dir": "sessions",
                "log_dir": "logs",
                "report_dir": "reports",
                "log_level": "INFO",
                "auto_retry": True
            },
            "plugins": {
                "enabled": [],
                "paths": []
            }
        }

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                default_config.update(config)
            except Exception as e:
                print(f"설정 로드 실패: {e}. 기본값 사용.")

        # API 키 환경 변수에서 로드
        default_config["api_settings"]["api_id"] = os.getenv("TELEGRAM_API_ID", default_config["api_settings"]["api_id"])
        default_config["api_settings"]["api_hash"] = os.getenv("TELEGRAM_API_HASH", default_config["api_settings"]["api_hash"])

        # 파일 권한 설정 (600)
        self.set_file_permissions()

        return default_config

    def save_config(self, config):
        """설정 저장"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.set_file_permissions()
            print("설정 저장 완료.")
        except Exception as e:
            print(f"설정 저장 실패: {e}")

    def set_file_permissions(self):
        """config.json 파일 권한을 600으로 설정"""
        try:
            subprocess.run(['icacls', CONFIG_FILE, '/inheritance:r'], check=True)
            subprocess.run(['icacls', CONFIG_FILE, '/grant:r', f"{os.getenv('USERNAME')}:F"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"파일 권한 설정 실패: {e}")

    def validate_config(self, config):
        """설정값 범위 제한"""
        limits = {
            "daily_per_account": (100, 500),
            "hourly_per_account": (50, 100),
            "personal_min_delay": (1, 2),
            "personal_max_delay": (2, 5),
            "group_min_delay": (2, 5),
            "group_max_delay": (5, 10),
            "max_concurrent_accounts": (1, 10)
        }

        for key, (min_val, max_val) in limits.items():
            if key in config["rate_limits"]:
                config["rate_limits"][key] = max(min_val, min(max_val, config["rate_limits"][key]))

        # priority_mode 유효성 검사
        valid_priorities = ["balanced", "sequential", "round_robin", "least_used"]
        if config["rate_limits"]["priority_mode"] not in valid_priorities:
            config["rate_limits"]["priority_mode"] = "balanced"

        # flood_wait_buffer 고정
        config["rate_limits"]["flood_wait_buffer"] = 60

        return config

    def update_config_field(self, key, value):
        """단일 설정값 업데이트"""
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            current = current[k]
        current[keys[-1]] = value
        self.config = self.validate_config(self.config)
        self.save_config(self.config)
