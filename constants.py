"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
           '(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
           'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}
