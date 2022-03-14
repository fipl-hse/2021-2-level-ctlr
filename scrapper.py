"""
Scrapper implementation
"""
import json
import os
import random
import re
import shutil
from collections import namedtuple
from time import sleep

import requests
from bs4 import BeautifulSoup

from constants import HEADERS


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


class BadStatusCode(Exception):
    """
    Custom error
    """


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.urls = []

    @staticmethod
    def _modify_link(link):
        if 'https://alp.iling.spb.ru/' not in link:
            link = 'https://alp.iling.spb.ru/' + link[2:]
        return link

    def _extract_url(self, article_bs):
        contents_bs = article_bs.select('div.content-cont-col-text a')
        links = [self._modify_link(article['href']) for article in contents_bs]
        return links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            sleep(random.randrange(2, 5))

            if not response.status_code == 200:
                raise BadStatusCode

            soup = BeautifulSoup(response.text, 'lxml')
            articles = self._extract_url(soup)[:self.total_max_articles]
            return articles

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

        n_articles = config['total_articles_to_find_and_parse']
        is_n_articles = isinstance(n_articles, int)
        is_n_in_range = is_n_articles and 0 < n_articles < 1000

        seed_urls = config['seed_urls']
        pattern = re.compile(r'https://alp\.iling\.spb\.ru/.+')
        is_seed_urls = all(pattern.match(str(seed)) for seed in seed_urls)

        Validation = namedtuple('Validation', ['success', 'error'])
        validations = (
            Validation(is_n_articles, IncorrectNumberOfArticlesError),
            Validation(is_n_in_range, NumberOfArticlesOutOfRangeError),
            Validation(is_seed_urls, IncorrectURLError)
        )

        for test in validations:
            if not test.success:
                raise test.error('Scrapper config check failed.')

        return seed_urls, n_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
