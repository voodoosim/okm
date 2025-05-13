import time
from collections import defaultdict
import random


class RateLimiter:
    """Rate limiting for Telegram API requests."""

    def __init__(
        self,
        daily_limit: int,
        hourly_limit: int,
        personal_min_delay: float,
        personal_max_delay: float,
        group_min_delay: float,
        group_max_delay: float,
        flood_wait_buffer: int,
        max_concurrent_accounts: int = 5  # 추가된 인자
    ):
        self.limits = {
            "daily_limit": daily_limit,
            "hourly_limit": hourly_limit,
            "personal_min_delay": personal_min_delay,
            "personal_max_delay": personal_max_delay,
            "group_min_delay": group_min_delay,
            "group_max_delay": group_max_delay,
            "flood_wait_buffer": flood_wait_buffer,
            "max_concurrent_accounts": max_concurrent_accounts
        }
        self.daily_counts = defaultdict(lambda: defaultdict(int))
        self.hourly_counts = defaultdict(lambda: defaultdict(int))
        self.minute_counts = defaultdict(lambda: defaultdict(int))
        self.last_message_time = defaultdict(float)
        self.message_counts = defaultdict(int)
        self.last_used = {}

    def get_limit(self, key: str) -> float:
        """Get a specific rate limit value."""
        return self.limits.get(key, 0)

    def can_send(self, account: str, chat_type: str) -> bool:
        """제한 체크"""
        date = time.strftime("%Y-%m-%d")
        hour = time.strftime("%Y-%m-%d-%H")
        minute = time.strftime("%Y-%m-%d-%H-%M")

        if self.daily_counts[date][account] >= self.limits["daily_limit"]:
            return False
        if self.hourly_counts[hour][account] >= self.limits["hourly_limit"]:
            return False
        minute_limit = 60 if chat_type == "personal" else 20
        if self.minute_counts[minute][account] >= minute_limit:
            return False
        return True

    def increment_counter(self, account: str) -> None:
        """카운터 증가"""
        date = time.strftime("%Y-%m-%d")
        hour = time.strftime("%Y-%m-%d-%H")
        minute = time.strftime("%Y-%m-%d-%H-%M")
        self.daily_counts[date][account] += 1
        self.hourly_counts[hour][account] += 1
        self.minute_counts[minute][account] += 1
        self.message_counts[account] += 1
        self.last_message_time[account] = time.time()
        self.last_used[account] = time.time()

    def get_next_available(self, accounts: list, priority: str, chat_type: str) -> list:
        """우선순위별 계정 선택"""
        available = [acc for acc in accounts if self.can_send(acc, chat_type)]
        if not available:
            return []
        if priority == "balanced":
            return sorted(
                available,
                key=lambda x: self.limits["daily_limit"] - self.daily_counts[time.strftime("%Y-%m-%d")][x],
                reverse=True
            )
        elif priority == "sequential":
            return available
        elif priority == "round_robin":
            return sorted(available, key=lambda x: self.last_used.get(x, 0))
        elif priority == "least_used":
            return sorted(available, key=lambda x: self.message_counts[x])
        return available

    def get_remaining_limits(self, account: str) -> dict:
        """남은 제한 반환"""
        date = time.strftime("%Y-%m-%d")
        hour = time.strftime("%Y-%m-%d-%H")
        minute = time.strftime("%Y-%m-%d-%H-%M")
        return {
            "daily": self.limits["daily_limit"] - self.daily_counts[date][account],
            "hourly": self.limits["hourly_limit"] - self.hourly_counts[hour][account],
            "minute_personal": 60 - self.minute_counts[minute][account],
            "minute_group": 20 - self.minute_counts[minute][account]
        }

    def get_delay(self, account: str, chat_type: str) -> float:
        """지연 계산"""
        now = time.time()
        last_time = self.last_message_time.get(account, 0)
        elapsed = now - last_time
        min_delay = self.limits["personal_min_delay"] if chat_type == "personal" else self.limits["group_min_delay"]
        max_delay = self.limits["personal_max_delay"] if chat_type == "personal" else self.limits["group_max_delay"]
        delay = random.uniform(min_delay, max_delay)
        return max(0, delay - elapsed)

    def handle_flood_wait(self, wait_time: int) -> int:
        """FloodWait 대기"""
        return wait_time + self.limits["flood_wait_buffer"]
