import customtkinter as ctk

def create_frame(parent, **kwargs):
    """공통 프레임 생성 헬퍼"""
    default_kwargs = {
        "corner_radius": 8,
        "fg_color": "transparent"
    }
    default_kwargs.update(kwargs)
    return ctk.CTkFrame(parent, **default_kwargs)

def create_button(parent, text, command, **kwargs):
    """공통 버튼 생성 헬퍼"""
    default_kwargs = {
        "width": 60,
        "height": 30,
        "fg_color": "transparent",
        "text_color": ("gray10", "gray90"),
        "hover_color": ("gray70", "gray30")
    }
    default_kwargs.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **default_kwargs)

def create_label(parent, text, **kwargs):
    """공통 라벨 생성 헬퍼"""
    default_kwargs = {
        "text_color": ("gray10", "gray90")
    }
    default_kwargs.update(kwargs)
    return ctk.CTkLabel(parent, text=text, **default_kwargs)
