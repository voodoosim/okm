import re

def validate_phone_number(phone):
    """전화번호 형식 검증 (+국가코드 포함)"""
    pattern = r"^\+\d{1,3}\d{6,12}$"
    if not re.match(pattern, phone):
        raise ValueError(f"잘못된 전화번호 형식: {phone}")
    return phone

def validate_target_id(target):
    """대상 ID 검증 (숫자 또는 @username)"""
    if isinstance(target, str):
        if target.startswith("@") and len(target) > 1:
            return target
        if target.startswith("-") and target[1:].isdigit():
            return target
        if target.isdigit():
            return target
    raise ValueError(f"잘못된 대상 ID: {target}")

def validate_session_name(name):
    """세션 이름 검증 (영숫자 및 밑줄)"""
    pattern = r"^[a-zA-Z0-9_]+$"
    if not re.match(pattern, name):
        raise ValueError(f"잘못된 세션 이름: {name}")
    return name
