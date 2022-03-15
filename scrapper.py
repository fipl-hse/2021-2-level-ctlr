"""
Scrapper implementation
"""
import json
import os

import requests
from bs4 import BeautifulSoup

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
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

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
        os.rmdir(base_path)
    except FileNotFoundError:
        pass
    os.mkdir(base_path)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        seed_urls = config['seed_urls']
        max_articles = config['total_articles_to_find_and_parse']

        if not isinstance(seed_urls, list):
            raise IncorrectURLError
        # если переменная seed_urls не является списком

        if not seed_urls:
            raise IncorrectURLError
        # возбуждает исключение, если такого seed_url
        # нет в списке, который мы сделали в scrapper_config.json

        if not isinstance(max_articles, int):
            raise IncorrectNumberOfArticlesError
        # если число статей, которое мы
        # передаем в scrapper_config.json не является integer

        if max_articles > 100:
            raise NumberOfArticlesOutOfRangeError
        # если статей для парсинга больше 100

        if max_articles == 0 or max_articles < 0:
            raise IncorrectNumberOfArticlesError
        # если число статей, которое мы
        # передаем в scrapper_config.json не является integer

        for seed_url in seed_urls:
            if seed_url[0:8] != 'https://' or seed_url[0:7] != 'http://':
                raise IncorrectURLError
        # если протокол не соответствует стандратному паттерну

        return seed_urls, max_articles
        # возвращает список urls и число статей


if __name__ == '__main__':
    # YOUR CODE HERE
    # with open(crawler_path) as file:
    #     config = json.load(file)
    # crawler = Crawler(seed_urls=seed_urls,
    #                   total_max_articles=max_articles)
