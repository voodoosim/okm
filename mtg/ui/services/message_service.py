class MessageService:
    def __init__(self, message_sender):
        self.message_sender = message_sender
        self.message_templates = {}

    def add_template(self, template_name, template_content):
        """메시지 템플릿 추가"""
        self.message_templates[template_name] = template_content

    def get_template(self, template_name):
        """메시지 템플릿 조회"""
        return self.message_templates.get(template_name)

    def preprocess_message(self, message):
        """메시지 전처리 (예: 특정 패턴 치환)"""
        # 예: {username} 패턴을 실제 사용자 이름으로 치환
        return message

    async def send_with_template(self, sessions, target, count, same_message, template_name, chat_type):
        """템플릿을 사용해 메시지 전송"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        messages = [self.preprocess_message(template)] if same_message else [self.preprocess_message(f"{template} #{i+1}") for i in range(count)]
        await self.message_sender.send_bulk(sessions, target, count, same_message, messages, chat_type)
