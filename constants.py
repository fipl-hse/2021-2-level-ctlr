"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'


HTTP_PATTERN = 'https://m.polit.ru'

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
           'accept': '*/*',
           'cookie': '_ym_uid=1641717784890293630; _ym_d=1641717784; __ddg1=V2XgNjxWDkMewjW2AaoX; '
                     '__ddg1_=V2XgNjxWDkMewjW2AaoX; _ym_isad=2; _ym_visorc=w; saw_cookie_warning=True',
           'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
           'origin': 'https: // m.polit.ru',
           'sec-ch-ua-mobile': '?0'
           }