"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
ROOT_URL = 'https://periodical.pstgu.ru'
HEADERS = {'cookie': 'swp_token=1529318441:da348e5038f36f4e22e839d6e317852a:c8fe351689c07b18b38cf1bb7e6604ff',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
           'Chrome/98.0.4758.119 YaBrowser/22.3.0.2430 Yowser/2.5 Safari/537.36'}
