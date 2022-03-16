"""
Scrapper implementation
"""

import json
import os
import re

from bs4 import BeautifulSoup
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, HEADERS
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
        content = article_bs.find_all('div', id='main-content')
        for article in content:
            all_links = article.find_all('a')

        for link in all_links:
            try:
                if link['href'][:4] == 'http':
                    self.urls.append(link['href'])
                else:
                    self.urls.append('https://vja.ruslang.ru' + link['href'])
            except KeyError:
                print('Incorrect link')

    def find_articles(self):
        """
        Finds articles
        """

        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)

            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

            '''
            with open(ASSETS_PATH, 'w', encoding='utf-8') as file:
                file.write(response.text)
            self.urls.append(url)
            '''

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(base_path)
    except FileNotFoundError:
        os.mkdir(base_path)


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

    if total_articles > 100:
        raise NumberOfArticlesOutOfRangeError

    pattern = re.compile(r"^https?://")

    for url in seed_urls:
        if not re.match(pattern, url):
            raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    return seed_urls, total_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
