class BaseWindow:
    """모든 윈도우/다이얼로그의 기본 클래스"""
    def __init__(self, parent=None):
        self.parent = parent
        if parent:
            self.root = parent.root
            self.config = parent.config
            self.event_logger = parent.event_logger
            self.monitor = parent.monitor
            self.dashboard = parent.dashboard
            self.rate_limiter = parent.rate_limiter
            self.session_manager = parent.session_manager
            self.message_sender = parent.message_sender
        else:
            self.root = None
            self.config = None
            self.event_logger = None
            self.monitor = None
            self.dashboard = None
            self.rate_limiter = None
            self.session_manager = None
            self.message_sender = None
