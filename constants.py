"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
           'accept': '*/*',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}
