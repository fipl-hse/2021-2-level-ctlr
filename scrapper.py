"""
Scrapper implementation
"""
import json
import os
import requests

from bs4 import BeautifulSoup

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
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
        class_bs = article_bs.find_all('div', class_= 'title')
        for title in class_bs:
            self.urls.append(title.find('a')['href'])

    def find_articles(self):
        """
        Finds articles
        """
        for urls in self.seed_urls:
            response = requests.get(urls)
            response.encoding = 'utf-16'
            #with open('index2.html', 'w', encoding='utf-16') as file:
            #     file.write(response.text)
            #print(response.status_code)
            #uwu
            article_bs = BeautifulSoup(response.text, features='html.parser')
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
        self.article = Article(article_url, article_id)

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()

        return self.article

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
    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls, max_articles)
    crawler.find_articles()
    print(crawler.urls)
  #  parser = ArticleParser(article_url=full_url, article_id=i)
