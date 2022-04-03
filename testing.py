import requests
from bs4 import BeautifulSoup

URL = 'https://snob.ru/theme/545/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.2.169 Yowser/2.5 Safari/537.36',
           'accept': '*/*'}

try:
    html_file = requests.get('https://snob.ru/theme/545/').text
    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(html_file)
except NameError:
    print('Website does not exist')
