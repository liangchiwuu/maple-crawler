"""
Settings and configuration for Maple Crawler.

Read values from conf.global_settings. See the global_settings.py for a list of
all possible variables. Don't alter any settings at runtime, the only place you
should assign to settings is in global_settings.py file.
"""

import os

from conf import global_settings


class Settings:
    def __init__(self):
        # update this dict from global settings (only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        # provide current project directory
        self.PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


settings = Settings()
