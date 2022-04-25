"""
Scrapper implementation
"""

import json
from pathlib import Path
import shutil

from bs4 import BeautifulSoup
import requests

from constants import (
    ASSETS_PATH,
    CRAWLER_CONFIG_PATH,
)
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
        for node in article_bs.find_all("a", {"class": "file"}):
            self.urls.append(node["href"])

    def find_articles(self):
        """
        Finds articles
        """
        for seed in self.seed_urls:
            response = requests.get(seed)
            article_bs = BeautifulSoup(response.text, features="html.parser")
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
        self.article = Article(url=article_url, article_id=article_id)

    def parse(self):
        # do things here
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, "html.parser")
        self._fill_article_with_text(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    assets = Path(base_path)
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True)


def validate_config(crawler_path: Path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config["seed_urls"]
    max_articles = config["total_articles_to_find_and_parse"]

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    seeds, limit = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seeds,
                      max_articles=limit)
    crawler.find_articles()

    for index, url in enumerate(crawler.urls):
        parser = HTMLParser(article_url=url, article_id=index)
        article = parser.parse()
