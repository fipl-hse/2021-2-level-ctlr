"""
Scrapper implementation
"""
import os
import json
import requests
from bs4 import BeautifulSoup



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
        class_bs = article_bs.find('div', class_='view-content view-rows')
        title_bs = class_bs.find_all('td', class_="views-field views-field-title table__cell")
        for link in title_bs:
            link = link.find('a')
            self.urls.append('https://rjano.ruslang.ru' + link['href'])


    def find_articles(self):
        """
        Finds articles
        """
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
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
    for seed_url in seed_urls:
        if seed_url[0:8] != 'https://' and seed_url[0:7] != 'http://':
            raise IncorrectURLError
    if not seed_urls:
        raise IncorrectURLError
    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    if max_articles == 0 or max_articles < 0:
        raise IncorrectNumberOfArticlesError
    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
