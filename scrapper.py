"""
Scrapper implementation
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from core_utils.article import Article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HEADERS#, URL_PATTERN


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
        response = requests.get('https://lingngu.elpub.ru/jour')
        with open('index.HTML', 'w', encoding='utf-8') as file:
            file.write(response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all('a', attrs={'href': re.compile("^http[s]?://")})
        for link in all_links:
            print(link.get('href'))
        #pass


    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            time.sleep(random.random())
            response = requests.get(seed_url, HEADERS)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls

class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find('div', class_='text')
        self.article.text = text_bs.text
        print(text_bs)


    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_text(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    pass


def validate_config(crawler_path):
    """
    Validates given config
    """
    pass


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
