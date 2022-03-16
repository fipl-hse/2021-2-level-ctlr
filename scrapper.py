"""
Scrapper implementation
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
from core_utils import article

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
        content = article_bs.find_all('div', id = '_id_article_listing')
        for article in content:
            all_links = article.find_all('a')
            for link in all_links:
                self.urls.append('https://gazeta.ru' + link ['href'])


    def find_articles(self):
        """
        Finds articles
        """
        pass

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass

class ArticleParser:
    def __init__(self, full_url, i):
        self.article_url = full_url
        self.article_id = i
        self.article = article.Article

    def _fill_article_with_text(self, article_bs):
        # self.article.save_raw()
        pass

    def parse(self):
        response = requests.get(self.article_url)
        response.encoding = 'utf-8'
        with open(f'{ASSETS_PATH}/{self.article_id}_article_url.html', 'w', encoding='utf-16') as file:
            file.write(response.text)
        with open(f'{ASSETS_PATH}/{self.article_id}_article_url.html', encoding='utf-16') as file:
            response = file.read()

        article_bs = BeautifulSoup(response, 'html.parser')





def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(ASSETS_PATH)
    except FileNotFoundError:
        os.mkdir(ASSETS_PATH)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as f:
        config = json.load(f)
    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']
    for url in seed_urls:
        correct_url = re.match(r'https://', url)
        if not correct_url:
            raise IncorrectURLError
    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError
    prepare_environment(ASSETS_PATH)
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE

    # seed_urls = config['seed_urls']
    # max_articles = config['total_articles']
    # crawler = Crawler(seed_urls=seed_urls, total_max_articles=max_articles)
    # crawler.find_articles()
    # parser = ArticleParser(article_url=full_url, article_id=i)

