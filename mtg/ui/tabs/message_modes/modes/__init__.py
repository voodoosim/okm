from pathlib import Path
import importlib

# 각 모드를 명시적으로 임포트
from .basic_mode import BasicMode
from .repeat_mode import RepeatMode
from .target_mode import TargetMode
from .toss_mode import TossModeTab as TossMode    # 별칭 추가
from .spam_mode import SpamModeTab as SpamMode    # 별칭 추가

__all__ = ["BasicMode", "RepeatMode", "TargetMode", "TossMode", "SpamMode"]

def load_all_modes():
    """모드를 동적으로 로드"""
    modes = {}
    current_dir = Path(__file__).parent

    for file in current_dir.glob("*.py"):
        if file.name != "__init__.py":
            module_name = file.stem
            try:
                module = importlib.import_module(f".{module_name}", package=__package__)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        hasattr(attr, 'get_metadata') and
                        attr.__name__.endswith('Mode')):
                        modes[attr.__name__] = attr
            except Exception as e:
                print(f"모드 로드 실패: {module_name} - {e}")

    return modes
