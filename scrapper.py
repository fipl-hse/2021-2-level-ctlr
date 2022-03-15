"""
Scrapper implementation
"""
import json
import os
import re
import requests
import time
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

    def __init__(self, seed_urls, total_max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }

        sleep_period = 5
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            time.sleep(sleep_period)

            if not response.ok:
                print("Request failed")

            with open(ASSETS_PATH / "index.html", 'w', encoding='utf-8') as file:
                file.write(response.text)

            with open('page_code.html', encoding='utf-8') as file:
                response = file.read()

            soup = BeautifulSoup(response, 'lxml')
            articles = soup.find("label", id="a2021")
            links = articles.find_all('a')
            self.urls = ["http://www.vestnik-mslu.ru/" + link['href'] for link in links]

            # articles = self._extract_url(soup)[:self.max_articles]
            # return articles

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class Article:
    def __init__(self, article):
        self.article = article


class ArticleParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id

    def parse(self):
        response = requests.get(self.article_url)
        with open(f'{ASSETS_PATH}/{self.article_id}_article.html', 'w') as file:
            file.write(response.text)

        article_bs = BeautifulSoup(response.text, 'lxml')

        # with open('page_code.html', encoding='utf-8') as file:
        #     response = file.read()
        return

    def _fill_article_with_text(self, article_bs):
        return None


# class PDFCrawler(HTMLCrawler):
#     pass


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
        config = json.load(file)

    seed_urls = config["seed_urls"]
    total_articles = config['total_articles']
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
    with open(CRAWLER_CONFIG_PATH) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    max_articles = config['total_articles']
    crawler = Crawler(seed_urls=seed_urls, total_max_articles=max_articles)

    crawler.find_articles()

    parser = ArticleParser(article_url=full_url, article_id=i)
