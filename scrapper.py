"""
Scrapper implementation
"""

import json
import os
import random
import re
import shutil
import time

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


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []
        self.domain = ""

    def _extract_url(self, article_bs):
        for article_link in article_bs.find_all("a", class_="article__download button-icon"):
            self.urls.append(''.join([self.domain, article_link.get("href")]))

    def find_articles(self):
        """
        Finds articles
        """
        domain = urlparse(self.seed_urls[0])
        self.domain = domain.scheme + "://" + domain.netloc + "/"

        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            if not response.ok:
                print("Request was unsuccessful.")
                continue

            article = BeautifulSoup(response.text, features="html.parser")
            self._extract_url(article)

            sleep_period = random.randrange(3, 7)
            time.sleep(sleep_period)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self._seed_urls


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

    urls = config["seed_urls"]
    articles = config["total_articles_to_find_and_parse"]
    http_regex = r'http[s]?://+\.ru/.+'

    if not urls:
        raise IncorrectURLError

    if not isinstance(articles, int):
        raise IncorrectNumberOfArticlesError

    if articles > 1000 or articles < 0:
        raise NumberOfArticlesOutOfRangeError

    for url in urls:
        check = re.search(http_regex, url)
        if not check:
            raise IncorrectURLError

    return urls, articles


class HTMLParser:

    def __init__(self, article_url, article_id):
        """
        Init
        """
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)


if __name__ == '__main__':
    outer_seed_urls, outer_max_articles = validate_config("scrapper_config.json")
    crawler = Crawler(outer_seed_urls, outer_max_articles)
    crawler.find_articles()
