import json
import time
import os
from collections import defaultdict

class Monitor:
    def __init__(self, log_dir, report_dir):
        self.log_dir = log_dir
        self.report_dir = report_dir
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

    def get_stats(self, date=None):
        """통계 계산"""
        if not date:
            date = time.strftime("%Y-%m-%d")

        stats = {
            "total": 0,
            "success": 0,
            "failure": 0,
            "accounts": defaultdict(lambda: {"success": 0, "failure": 0})
        }

        message_log_file = os.path.join(self.log_dir, f"{date}_messages.json")
        if os.path.exists(message_log_file):
            try:
                with open(message_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        log = json.loads(line.strip())
                        stats["total"] += 1
                        account = log.get("account", "unknown")
                        if log["event_type"] == "message_sent":
                            stats["success"] += 1
                            stats["accounts"][account]["success"] += 1
                        else:
                            stats["failure"] += 1
                            stats["accounts"][account]["failure"] += 1
            except Exception as e:
                print(f"통계 계산 실패: {e}")

        return stats

    def generate_daily_report(self):
        """일일 리포트 생성"""
        date = time.strftime("%Y-%m-%d")
        stats = self.get_stats(date)

        report_file = os.path.join(self.report_dir, f"{date}_report.txt")
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"텔레그램 멀티컨트롤 일일 리포트 ({date})\n")
                f.write("=" * 40 + "\n")
                f.write(f"총 전송 시도: {stats['total']}회\n")
                f.write(f"성공: {stats['success']}회\n")
                f.write(f"실패: {stats['failure']}회\n")
                f.write("\n계정별 통계:\n")
                for account, acc_stats in stats["accounts"].items():
                    f.write(f"- {account}: 성공 {acc_stats['success']}, 실패 {acc_stats['failure']}\n")
            print(f"일일 리포트 저장: {report_file}")
        except Exception as e:
            print(f"리포트 생성 실패: {e}")
