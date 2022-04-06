"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'


HTTP_PATTERN = 'https://www.vedomosti.ru'
HTTP_PATTERN1 = 'https://www.vedomosti.ru/rubrics'


