"""
Default global settings for Maple Crawler.

You should NOT import from global_settings.py directly. Use settings by importing
the object conf.settings. Example: from conf import settings. The settings object
abstracts the concepts of default settings and presents a single interface.
"""

# url setting
MAPLETUNES_RANDOM_PLAYER = 'https://maplebgm.cc/bgmplayer_rand.php'
MAPLETUNES_URL = 'https://maplebgm.cc/'

# directory setting
DOWNLOAD_DIR = 'downloads'
LOG_DIR = 'logs'
