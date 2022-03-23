"""
Scrapper implementation
"""
import datetime
import re
import shutil

import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
from core_utils.article import Article


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
        urls_bs = article_bs.find_all('a', class_="cardWrap_link__2AN_X")
        the_beginning = 'https://tass.ru'
        urls_bs_full = []
        for url_bs in urls_bs:
            the_end = url_bs['href']
            url_select = f'{the_beginning}{the_end}'
            urls_bs_full.append(url_select)
        for full_url in urls_bs_full:
            if len(self.urls) < self.max_articles:
                self.urls.append(full_url)

        return urls_bs_full

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url)
            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.find('h1').text

        self.article.author = 'NOT FOUND'

        date_epoch = article_bs.dateformat['time']
        self.article.date = datetime.datetime.fromtimestamp(int(date_epoch))

        if article_bs.find('a', class_='tags__item'):
            self.article.topic = article_bs.find('a', class_='tags__item').text

    def _fill_article_with_text(self, article_bs):
        text_content = article_bs.find('div', class_="text-content")
        divs = text_content.find_all('div', class_="text-block")
        self.article.text = ''
        for div in divs:
            ps = div.find_all('p')
            for p in ps:
                self.article.text += p.text.strip()

    def parse(self):
        response = requests.get(url=self.article_url)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    seed_urls = configuration['seed_urls']
    max_articles = configuration['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    part_of_string = re.compile(r'^https?://')
    for seed_url in seed_urls:
        if not part_of_string.search(seed_url):
            raise IncorrectURLError

    return seed_urls, max_articles


if __name__ == '__main__':
    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls, max_articles)
    crawler.find_articles()

    ID = 0
    for article_url_text in crawler.urls:
        ID += 1
        article_parser = HTMLParser(article_url_text, ID)
        article = article_parser.parse()
        article.save_raw()
