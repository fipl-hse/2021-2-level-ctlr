import datetime
import json
from pathlib import Path
import re
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile
from constants import HEADERS, HTTP_PATTERN, ASSETS_PATH, CRAWLER_CONFIG_PATH, MONTHS_DICT

# text = 'Фразеологизмы, основанные на псевдоисчерпании, в говорах Низовой Печоры | Вестн. Том. гос. ун-та. Филология. 2021. № 73. DOI: 10.17223/19986645/73/8'
# pattern = re.compile(r'№ \d+')
# matcht = pattern.search(text)
# number_of_pub = matcht.group(0).replace(' ', '')
#
# response = requests.get('http://journals.tsu.ru/philology/&journal_page=archive', headers=HEADERS)
# article_bs = BeautifulSoup(response.text, 'lxml')
# table = article_bs.find('table')
# rows = table.find_all('tr')
# months = rows[0].find_all('td')
# month_number = 0
# for row in rows:
#     cells = row.find_all('td')
#     for index, cell in enumerate(cells):
#         if number_of_pub in cell.text and not month_number:
#             month_number = index
#             break
# month = months[month_number].text
# print(month)