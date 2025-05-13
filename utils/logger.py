import os
from loguru import logger
import time
import json

class EventLogger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # loguru 설정
        logger.remove()  # 기본 핸들러 제거
        date = time.strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{date}_messages.json")

        # JSON 로그 파일 출력
        logger.add(
            log_file,
            format="{message}",
            level="INFO",
            serialize=True,
            rotation="500 MB",
            retention="30 days"
        )
        # 에러 로그 파일
        logger.add(
            os.path.join(self.log_dir, f"{date}_errors.json"),
            level="ERROR",
            serialize=True,
            rotation="50 MB"
        )

    def write_log(self, event_type, data):
        """JSON 로그 작성"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "event_type": event_type,
            **data
        }
        logger.info(json.dumps(log_entry, ensure_ascii=False))

    def on_message_sent(self, event_data):
        self.write_log("message_sent", event_data)

    def on_rate_limit_hit(self, event_data):
        self.write_log("rate_limit_hit", event_data)

    def on_account_switched(self, event_data):
        self.write_log("account_switched", event_data)

    def on_session_created(self, event_data):
        self.write_log("session_created", event_data)

    def on_error_occurred(self, event_data):
        self.write_log("error_occurred", event_data)

    def on_flood_wait(self, event_data):
        self.write_log("flood_wait", event_data)
