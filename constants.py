"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
DOMAIN = "http://journal.asu.ru/urisl/"
BLACK_LIST = [
    "http://journal.asu.ru/urisl/article/view/%282021%292001",
    "http://journal.asu.ru/urisl/article/view/10494",
    "http://journal.asu.ru/urisl/article/view/10491",
    "http://journal.asu.ru/urisl/article/view/%282021%292102",
    "http://journal.asu.ru/urisl/article/view/%282021%292101",
    "http://journal.asu.ru/urisl/article/view/%282021%292105",
    "http://journal.asu.ru/urisl/article/view/%282021%292104",
    "http://journal.asu.ru/urisl/article/view/%282020%291605",
    "http://journal.asu.ru/urisl/article/view/%282020%291505",
    "http://journal.asu.ru/urisl/article/view/9-1005",
    "http://journal.asu.ru/urisl/article/view/7-809",
    "http://journal.asu.ru/urisl/article/view/503",
    "http://journal.asu.ru/urisl/article/view/505",
    "http://journal.asu.ru/urisl/article/view/512",
    "http://journal.asu.ru/urisl/article/view/514"
]
