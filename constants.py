"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
ROOT_URL = "http://www.vestnik.unn.ru/"
RUSSIAN_ROOT_URL = ROOT_URL + 'ru'
DOMAIN_URL = RUSSIAN_ROOT_URL + "/nomera"
RAW_FILE_PATH_ENDING = '_raw.txt'
