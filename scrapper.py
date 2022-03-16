"""
Scrapper implementation
"""
import json
import os
import requests
from bs4 import BeautifulSoup
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
#from core_utils.article import Article

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
        class_bs = article_bs.find('div', class_="b-materials-list b-list_infinity")
        title_bs = class_bs.find_all('p', class_="b-materials-list__title b-materials-list__title_news")
        for link in title_bs:
            link = link.find('a')
            self.urls.append('https://magadanpravda.ru/' + link['href'])

    def find_articles(self):
        """
        Finds articles
        """
        for urls in self.seed_urls:
            response = requests.get(urls)
            response.encoding = 'utf-16'
            with open('index.html', 'w', encoding='utf-16') as file:
                 file.write(response.text)
            print(response.status_code)
            article_bs = BeautifulSoup(response.text, features='html.parser')
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
    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    for urls in seed_urls:
        if urls[0:8] != 'https://' and urls[0:7] != 'http://':
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
