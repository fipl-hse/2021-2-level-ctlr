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
           'sec-ch-ua': " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100",
           'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': "Windows",
           'sec-fetch-dest': 'empty',
           'sec-fetch-mode': 'cors',
           'sec-fetch-site': 'cross-site',
           'cookie': 'yandexuid=5687879911644746701; yuidss=5687879911644746701; '
                     'ymex=1960108130.yrts.1644748130#1960108129.yrtsi.1644748129; '
                     'is_gdpr=0; _ym_uid=1645129214159782619; is_gdpr_b=CPrlYRD4ZSgC; '
                     'my=YwA=; yandex_gid=47; _ym_d=1650977028; MGphYZof=1; computer=1; '
                     'yabs-frequency=/5/0000000000000000/teR6PWWKsNz8HY5wlnSwdWwCTaX68RMKMpnRSMDS'
                     'I4OZ8krF10oancv8HYDZIlIyL2gUU4X6WDgIfCn34kfoI4OW/; i=SyudZhTUgwGo4+aw44K2ho/vDU6zcg'
                     'sazAkrcqDNh2YeB9K6HAa6xdtqD5CLFLY0JdVHajOmsCRfbHh+KYq0NzFreWQ=; yabs-sid=2627592021651080827'}
