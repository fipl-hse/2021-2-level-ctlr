"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
           'accept-encoding': 'gzip, deflate',
           'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7', 'cookie': '__ddgid=wa1QimjPWTUeFFaV; '
                                                                               '_ym_uid=1646637420743462688; '
                                                                               '_ym_d=1646637420; '
                                                                               '__ddg2=6zjt8EXnstReWrFv; '
                                                                               '__ddgmark=PGOvWm6dcTwlOrTJ; '
                                                                               '_ym_isad=2; '
                                                                               '__ddg1=spn9kmJyPatskoSI11V3; '
                                                                               '__ddg5=jhLAL3PJiAIxwzWb; _ym_visorc=b '}
DOMAIN_NAME = 'https://iz.ru/'
