import asyncio
import time
import os
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, PhoneNumberBannedError
from telethon.tl.types import User, Channel, Chat
from utils.validators import validate_target_id
from utils.retry import retry_with_backoff

class MessageSender:
    def __init__(self, session_dir, api_id, api_hash, rate_limiter, event_logger, dashboard):
        self.session_dir = session_dir
        self.api_id = api_id
        self.api_hash = api_hash
        self.rate_limiter = rate_limiter
        self.event_logger = event_logger
        self.dashboard = dashboard
        self.semaphore = asyncio.Semaphore(self.rate_limiter.config["rate_limits"]["max_concurrent_accounts"])

    async def detect_chat_type(self, client, target):
        """채팅 타입 감지"""
        try:
            entity = await client.get_entity(target)
            if isinstance(entity, User):
                return "personal"
            elif isinstance(entity, (Channel, Chat)):
                return "group"
        except Exception as e:
            print(f"채팅 타입 감지 실패: {e}. 기본값 'group' 사용.")
            self.event_logger.on_error_occurred({"error": str(e), "target": target})
            return "group"
        return "group"

    async def send_message(self, client, target, message, chat_type):
        """단일 메시지 전송"""
        start_time = time.time()
        response_time = 0
        try:
            await client.send_message(target, message)
            response_time = (time.time() - start_time) * 1000  # ms 단위
            return True, response_time
        except FloodWaitError as e:
            wait_time = self.rate_limiter.handle_flood_wait(e.seconds)
            self.event_logger.on_flood_wait({"wait_time": wait_time, "target": target})
            await asyncio.sleep(wait_time)
            await client.send_message(target, message)
            response_time = (time.time() - start_time) * 1000
            return True, response_time
        except Exception as e:
            self.event_logger.on_error_occurred({"error": str(e), "target": target})
            return False, response_time

    async def send_bulk(self, sessions, target, total_messages, same_message=True):
        """다중 계정으로 메시지 전송"""
        target = validate_target_id(target)

        # 채팅 타입 결정
        chat_type = input("채팅 타입 (personal/group, Enter로 자동 감지): ").strip().lower()
        if chat_type not in ["personal", "group"]:
            async with TelegramClient(os.path.join(self.session_dir, sessions[0]["name"]), self.api_id, self.api_hash) as client:
                chat_type = await self.detect_chat_type(client, target)
        print(f"채팅 타입: {chat_type}")

        # 메시지 입력
        messages = []
        if same_message:
            message = input("보낼 메시지: ").strip()
            messages = [message] * total_messages
        else:
            print(f"계정마다 다른 메시지를 입력하세요 (총 {total_messages}개 메시지):")
            for i in range(total_messages):
                messages.append(input(f"메시지 {i+1}: ").strip())

        sent_messages = 0
        remaining_messages = total_messages
        account_ids = [f"{s['username']} (...{s['phone']})" for s in sessions]

        print(f"총 {total_messages}회 메시지 전송 시작 (계정 수: {len(sessions)}, 우선순위: {self.rate_limiter.config['rate_limits']['priority_mode']})")

        while remaining_messages > 0 and account_ids:
            available_accounts = self.rate_limiter.get_next_available(account_ids, self.rate_limiter.config["rate_limits"]["priority_mode"], chat_type)
            if not available_accounts:
                print("모든 계정이 제한에 도달했습니다. 작업 종료.")
                self.event_logger.on_rate_limit_hit({"accounts": account_ids})
                break

            tasks = []
            for i, account_id in enumerate(available_accounts):
                next_account = available_accounts[(i + 1) % len(available_accounts)] if len(available_accounts) > 1 else None
                session = next(s for s in sessions if f"{s['username']} (...{s['phone']})" == account_id)
                session_path = os.path.join(self.session_dir, session['name'])

                async def send_task():
                    async with self.semaphore:
                        if not self.rate_limiter.can_send(account_id, chat_type):
                            self.event_logger.on_rate_limit_hit({"account": account_id})
                            return False, 0

                        delay = self.rate_limiter.get_delay(account_id, chat_type)
                        if delay > 0:
                            await asyncio.sleep(delay)

                        async with TelegramClient(session_path, self.api_id, self.api_hash) as client:
                            message = messages[sent_messages % len(messages)]
                            start_time = time.time()
                            try:
                                success, response_time = await retry_with_backoff(
                                    self.send_message,
                                    max_attempts=3,
                                    client=client,
                                    target=target,
                                    message=message,
                                    chat_type=chat_type
                                )
                            except PhoneNumberBannedError as e:
                                account_ids.remove(account_id)
                                self.event_logger.on_error_occurred({"error": str(e), "account": account_id})
                                return False, 0

                            network_latency = (time.time() - start_time) * 1000 - response_time

                            if success:
                                self.rate_limiter.increment_counter(account_id)
                                limits = self.rate_limiter.get_remaining_limits(account_id)
                                self.event_logger.on_message_sent({
                                    "account": account_id,
                                    "target": target,
                                    "message": message,
                                    "limits": limits,
                                    "next_account": next_account,
                                    "performance": {
                                        "message_delay": delay,
                                        "api_response_time": response_time,
                                        "network_latency": network_latency
                                    }
                                })
                                print(f"계정 {account_id} - 메시지 {sent_messages + 1}/{total_messages} 전송 완료")
                                return True, 1
                            else:
                                return False, 0

                tasks.append(send_task())

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for success, count in results:
                if success:
                    sent_messages += count
                    remaining_messages -= count
                    self.event_logger.on_account_switched({"current_account": available_accounts[0], "next_account": available_accounts[1] if len(available_accounts) > 1 else None})
                    self.dashboard.render(total_messages, sent_messages, account_ids, self.rate_limiter, chat_type)

            await asyncio.sleep(1)  # 계정 간 쿨다운

        print(f"전송 완료: {sent_messages}/{total_messages} 메시지 전송")
