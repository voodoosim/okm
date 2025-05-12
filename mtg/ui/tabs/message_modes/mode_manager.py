import os
import importlib
import logging
from tkinter import messagebox

class ModeManager:
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.available_modes = self.scan_modes()
        self.loaded_modes = {}
        self.logger.info(f"스캔된 모드: {list(self.available_modes.keys())}")

    def scan_modes(self):
        """사용 가능한 모든 모드 스캔"""
        modes_dir = os.path.join(os.path.dirname(__file__), 'modes')
        available_modes = {}

        for filename in os.listdir(modes_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'.modes.{module_name}', package='ui.tabs.message_modes')
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            hasattr(attr, 'get_metadata') and
                            hasattr(attr, 'create') and
                            attr.__name__.endswith('Mode') and
                            attr.__name__ != 'BaseMode'):
                            metadata = attr.get_metadata()
                            available_modes[metadata.name] = (attr, metadata)
                except Exception as e:
                    self.logger.error(f"모드 스캔 실패: {filename} - {e}")

        return available_modes

    def load_mode(self, mode_name):
        """특정 모드 로드"""
        if mode_name not in self.available_modes:
            return None

        if mode_name not in self.loaded_modes:
            mode_class, metadata = self.available_modes[mode_name]
            mode_instance = mode_class(self.parent)
            self.loaded_modes[mode_name] = (mode_instance, metadata)

        return self.loaded_modes[mode_name]

    def create_tab(self, tabview, mode_name):
        """선택된 모드 탭 생성"""
        mode_data = self.load_mode(mode_name)
        if mode_data:
            try:
                mode_instance, metadata = mode_data
                tabview.add(mode_name)
                tab = tabview.tab(mode_name)
                mode_instance.create(tab)
                mode_instance.create_mode_description(tab, metadata)
                self.logger.info(f"모드 탭 생성 완료: {mode_name}")
            except Exception as e:
                self.logger.error(f"모드 탭 생성 실패: {mode_name} - {e}")
                messagebox.showerror("오류", f"모드 로드 실패: {mode_name}")
