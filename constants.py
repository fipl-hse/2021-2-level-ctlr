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
           'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
           'cookie': 'yandexuid=5687879911644746701; yuidss=5687879911644746701; '
                     'ymex=1960108130.yrts.1644748130#1960108129.yrtsi.1644748129; '
                     'is_gdpr=0; _ym_uid=1645129214159782619; is_gdpr_b=CPrlYRD4ZSgC; '
                     '_ym_d=1646573834; my=YwA=; i=O/LSyUkDVItvP6mrxwFvhLiSwuukrl5QrxYX'
                     'rjVo+z2gpcFOFTc3Yj4ZSE7HnZvC9yiHvr7pgMQHPgPx0SzsMwhMBoE=; '
                     'skid=3746917891646583925; yabs-frequency=/5/0000000000000000/Oqhql'
                     '5GgddXyHM3QagJCGnBgSdn58Fzy-QAONRbNV4KX5Hn1ROO0001yHIE2OK5jXW0007n58'
                     'm00/; yabs-sid=2303709261650966773'}
