"""
Scrapper implementation
"""
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH


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
        self.max_articles = max_articles
        self.seed_urls = seed_urls
        self.urls = []

    def _extract_url(self, article_bs):
        urls_bs = article_bs.find_all('a', class_="item__link")
        begin_link = "https://www.rbc.ru/"
        urls_bs_all = []

        for url_bs in urls_bs:
            end_link = url_bs['href']
            urls_bs_all.append(f'{begin_link}{end_link}')

        return urls_bs_all

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url)

            if not response.ok:
                continue

            soup_lib = BeautifulSoup(response.text, 'lxml')
            article_urls = self._extract_url(soup_lib)
            for article_url in article_urls:
                self.urls.append(article_url)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.removedirs(base_path)
    except FileNotFoundError:
        pass
    finally:
        os.makedirs(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    total_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError
    for article_url in seed_urls:
        correct_url = re.match(r'https://', article_url)  # looking for pattern in the string
        if not correct_url:
            raise IncorrectURLError

    if total_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    if not isinstance(total_articles, int) or total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    return seed_urls, total_articles


if __name__ == '__main__':
    seed_urls, total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_urls, max_articles=total_articles)
    crawler.find_articles()
