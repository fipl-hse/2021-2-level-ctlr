"""
Scrapper implementation
"""
import json
import os
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HEADERS
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

    def __init__(self, seed_urls, total_max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        article_summaries = article_bs.find("div", class_="obj_article_summary")
        articles = article_summaries.find("div", class_="title")
        for link in articles:
            self.urls.append(link.find('a')['href'])

    def find_articles(self):
        """
        Finds articles
        """
        sleep_period = 5
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            sleep(sleep_period)

            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class ArticleParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        response = requests.get(self.article_url, headers=HEADERS)
        with open(f'{ASSETS_PATH}/{self.article_id}_article.html', 'w') as file:
            file.write(response.text)

    def _fill_article_with_text(self, article_bs):
        return None


# class PDFCrawler(HTMLCrawler):
#     pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if ASSETS_PATH.exists():
        ASSETS_PATH.unlink()
    try:
        os.removedirs(ASSETS_PATH)
    except FileNotFoundError:
        pass
    os.makedirs(ASSETS_PATH)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config["seed_urls"]
    total_articles = config['total_articles_to_find_and_parse']

    pattern = re.compile(r"^https?://")

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    for url in seed_urls:
        if not pattern.search(url):
            raise IncorrectURLError

    return seed_urls, total_articles


if __name__ == '__main__':
    # with open(CRAWLER_CONFIG_PATH) as file:
    #     config = json.load(file)
    #
    # seed_urls = config['seed_urls']
    # max_articles = config['total_articles']
    # crawler = Crawler(seed_urls=seed_urls, total_max_articles=max_articles)
    #
    # crawler.find_articles()
    #
    # parser = ArticleParser(article_url=full_url, article_id=i)
    prepare_environment(ASSETS_PATH)
