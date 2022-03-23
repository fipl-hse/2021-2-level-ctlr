"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
              'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Acccept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}
HTTP_PATTERN = 'http://journals.tsu.ru'

MONTHS_DICT = {('№ 69', '№ 63', '№ 57', '№ 51', '№ 45', '№1 (39)', '№1 (33)', '№1 (27)', '№1 (21)'): '2',
               ('№ 70', '№ 64', '№ 58', '№ 52', '№ 46', '№1 (40)', '№1 (34)', '№1 (28)', '№1 (22)'): '4',
               ('№ 71', '№ 65', '№ 59', '№ 53', '№ 47', '№1 (41)', '№1 (35)', '№1 (29)', '№1 (23)'): '4',
               ('№ 72', '№ 66', '№ 60', '№ 54', '№ 49', '№1 (42)', '№1 (36)', '№1 (30)', '№1 (24)'): '6',
               ('№ 73', '№ 67', '№ 61', '№ 55', '№ 50', '№1 (43)', '№1 (37)', '№1 (31)', '№1 (25)'): '8',
               ('№ 74', '№ 68', '№ 62', '№ 56', '№ 51', '№1 (44)', '№1 (38)', '№1 (32)', '№1 (26)'): '10'}
