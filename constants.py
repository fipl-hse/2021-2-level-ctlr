"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ASSETS_PATH = PROJECT_ROOT / 'tmp' / 'articles'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'scrapper_config.json'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/98.0.4758.102 Safari/537.36'}
ISSUE_YEARS = {'xvii': '2021', 'xvi': '2020', 'xv': '2019', 'xiv': '2018', 'xiii': '2017',
               'xii': '2016', 'xi': '2015', 'x': '2014', 'ix': '2013', 'viii': '2012',
               'vii': '2011', 'vi': '2010', 'v': '2009', 'iv': '2008', 'iii': '2007', 'ii': '2006'}
ISSUE_MONTHS = {'1': '01', '2': '05', '3': '09'}
