from termcolor import colored
from tqdm import tqdm
import time

class Dashboard:
    def __init__(self, update_interval=10):
        self.update_interval = update_interval
        self.last_update = 0
        self.progress_bar = None

    def render(self, total_messages, sent_messages, accounts, limiter, chat_type):
        """대시보드 렌더링"""
        if time.time() - self.last_update < self.update_interval and sent_messages % 5 != 0:
            return

        progress = (sent_messages / total_messages * 100) if total_messages > 0 else 0
        if not self.progress_bar:
            self.progress_bar = tqdm(total=total_messages, desc="진행률", unit="msg")
        self.progress_bar.n = sent_messages
        self.progress_bar.refresh()

        print("\n" + "=" * 60)
        print(f"텔레그램 멀티컨트롤 대시보드 ({time.strftime('%Y-%m-%d %H:%M:%S')})")
        print("=" * 60)
        print(f"진행률: {sent_messages}/{total_messages} ({progress:.1f}%)")
        print(f"성공: {sent_messages} | 실패: {0}")  # 실패는 monitor에서 계산

        print("\n계정 상태:")
        print("-" * 60)
        print(f"{'계정':<20} {'상태':<10} {'일일 남음':<12} {'시간당 남음':<12} {'분당 남음':<12}")
        print("-" * 60)
        for account in accounts:
            limits = limiter.get_remaining_limits(account)
            status = "활성" if limiter.can_send(account, chat_type) else "제한"
            minute_limit = limits["minute_personal"] if chat_type == "personal" else limits["minute_group"]
            status_color = "green" if status == "활성" else "red"
            print(colored(f"{account:<20} {status:<10} {limits['daily']:<12} {limits['hourly']:<12} {minute_limit:<12}", status_color))
        print("=" * 60)

        self.last_update = time.time()
