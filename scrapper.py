"""
Scrapper implementation
"""

from urllib.parse import urlparse
from urllib.parse import urljoin
import json
import os
import datetime
import shutil
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH
from constants import ASSETS_PATH

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

class HTMLParser:
    """
    An entity that is responsible for extraction of all needed information from a single article web page.
    """

    article_url = ''
    article_id = 0

    article = None

    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)

    def parse(self):
        html = requests.get(self.article_url).text
        article_bs = BeautifulSoup(html, 'html.parser')
        self._fill_article_with_text(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        self.article.title = article_bs.find('h1').text
        self.article.text = ' '.join(data.text for data in article_bs.find_all('div', {'class': 'post post2'}))
        self.article.author = article_bs.find('a', {'rel': 'nofollow'}).text
        self.article.date = datetime.datetime.today()


class Crawler:
    """
    Crawler implementation
    """
    seed_urls = []
    max_articles = 0
    urls = []
    def __init__(self, seed_urls, max_articles: int):
        self.seed_urls = seed_urls
        self.max_articles = max_articles
        pass

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            if self.seed_urls.index(url) < self.max_articles:
                html = requests.get(url).text
                self.exctract_aticle_urls(url, html)
            else:
                break


    def exctract_aticle_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            _is_url_by_user = (self._is_string_contains(path, 'community') or self._is_string_contains(path, 'user'))
            _is_url_valid_content = self._is_string_contains(path, 'content')
            _is_url_not_comment = _is_url_valid_content and not self._is_string_contains(path, 'comment')
            if path and path.startswith('/') and _is_url_by_user and _is_url_not_comment:
                path = urljoin(url, path)
                self.urls.append(path)

    def _is_string_contains(self, source_string, substring):
        return source_string.find(substring) != -1

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path)
    os.makedirs(base_path)


def validate_config(crawler_path):
    file = open(crawler_path)
    dict_data = json.load(file)
    seed_urls = dict_data["seed_urls"]
    total_articles_to_find_and_parse = dict_data["total_articles_to_find_and_parse"]

    if seed_urls:
        for url in seed_urls:
            validate_url(url)
    else:
        raise ValueError("No urls")

    is_number_of_articles_valid(total_articles_to_find_and_parse)
    is_number_of_articles_in_range(3, total_articles_to_find_and_parse)
    return seed_urls, total_articles_to_find_and_parse

def validate_url(url):
    result = urlparse(url)
    if (isinstance(url,str) and url != "" and all([result.scheme, result.netloc])):
        pass
    else:
        raise IncorrectURLError()

def is_number_of_articles_in_range(number, range_number):
    if number <= range_number:
        pass
    else:
        raise NumberOfArticlesOutOfRangeError()

def is_number_of_articles_valid(number):
    if isinstance(number, int):
        pass
    else:
        raise IncorrectNumberOfArticlesError()


if __name__ == '__main__':
    _seed_urls, _max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=_seed_urls, max_articles=_max_articles)
    crawler.find_articles()
    print(len(crawler.urls))
    articles_to_save = []
    for i in range(_max_articles):
        _url = crawler.urls[i]
        parser = HTMLParser(article_url=_url, article_id=crawler.urls.index(_url))
        article = parser.parse()
        articles_to_save.append(article)
    for article in articles_to_save:
        article.save_raw()
        article.save_raw()

