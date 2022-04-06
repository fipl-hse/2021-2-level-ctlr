"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)'
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.119 Mobile Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru,en;q=0.9,de;q=0.8',
        }
