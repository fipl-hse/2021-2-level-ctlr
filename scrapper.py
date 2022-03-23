"""
Scrapper implementation
"""

import datetime
import json
import random
import re
import shutil
import time

from bs4 import BeautifulSoup
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, HEADERS
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile


class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Total number of articles to parse is too big
    """


class IncorrectNumberOfArticlesError(Exception):
    """
    Total number of articles to parse in not integer
    """


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        content = article_bs.find('div', {'class': 'node__container'})
        urls = content.find_all('a')

        for url in urls:
            if len(self.urls) < self.max_articles:
                if 'https://vja.ruslang.ru' + url['href'] not in self.urls:
                    self.urls.append('https://vja.ruslang.ru' + url['href'])
            else:
                break

    def find_articles(self):
        """
        Finds articles
        """

        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            time.sleep(random.randrange(2, 6))

            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        link = article_bs.find('iframe', {'class': 'pdf'})['data-src']

        pdf = PDFRawFile(link, self.article_id)
        pdf.download()
        full_article = pdf.get_text()

        if 'СПИСОК ЛИТЕРАТУРЫ' in full_article:
            full_article = full_article.split('СПИСОК ЛИТЕРАТУРЫ')[0]
        elif 'REFERENCES' in full_article:
            full_article = full_article.split('REFERENCES')[0]

        self.article.text = full_article

    def _fill_article_with_meta_information(self, article_bs):
        article_title = article_bs.find('title').text
        self.article.title = article_title

        article_author = article_bs.find('strong').text
        if not article_author:
            article_author = 'NOT FOUND'
        if '\n' in article_author:
            article_author = article_author.split('\n')[0]
        self.article.author = article_author.strip()

        meta_inf = re.findall(r'\d.+', article_bs.find('link', rel='alternate')['href'])[0]
        year = meta_inf[:4]
        volume = meta_inf[5]
        months_dict = {'1': '01', '2': '03', '3': '05', '4': '07', '5': '09', '6': '11'}
        month = months_dict[volume]
        date_raw = f'{year}-{month}'
        article_date = datetime.datetime.strptime(date_raw, '%Y-%m')
        self.article.date = article_date


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    total_articles = config['total_articles_to_find_and_parse']

    if not isinstance(total_articles, int) or total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    pattern = re.compile(r"^https?://")

    for url in seed_urls:
        if not re.match(pattern, url):
            raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    prepare_environment(ASSETS_PATH)

    return seed_urls, total_articles


if __name__ == '__main__':
    given_seed_urls, all_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(given_seed_urls, all_articles)
    crawler.find_articles()

    for i, current_url in enumerate(crawler.urls):
        parser = HTMLParser(current_url, i + 1)
        article = parser.parse()
        article.save_raw()
