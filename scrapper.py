"""
Scrapper implementation
"""
import json
import os
import re

import requests

from constants import ASSETS_PATH


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
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,applicat '
                      'ion/signed-exchange;v=b3;q=0.9',
            'Acccept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        for url in self.seed_urls:
            response = requests.get(url=url, headers=headers)
            with open(ASSETS_PATH, 'w', encoding='utf-8') as file:
                file.write(response.text)
            self.urls.append(url)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(ASSETS_PATH)
    except FileNotFoundError:
        pass
    os.mkdir(ASSETS_PATH)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    seed_urls = configuration["seed_urls"]
    total_articles = configuration["total_articles_to_find_and_parse"]
    http_pattern = re.compile(r'^https?://')
    for url in seed_urls:
        result = http_pattern.search(url)
        if not result:
            raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    # with open(crawler_path) as file:
    #     config = json.load(file)
    # crawler = Crawler(seed_urls=seed_urls,
    #                   total_max_articles=max_articles)
    pass
