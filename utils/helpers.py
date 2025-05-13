import time

def format_timestamp():
    """ISO 형식 타임스탬프 반환"""
    return time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def sanitize_input(text):
    """입력에서 위험 문자 제거"""
    return text.replace('\n', '').replace('\r', '').strip()
