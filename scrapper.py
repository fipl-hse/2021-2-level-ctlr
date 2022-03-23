"""
Scrapper implementation
"""
import json
import re
import shutil
from pathlib import Path
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
        self.max_articles = max_articles
        self.seed_urls = seed_urls
        self.urls = []

    def _extract_url(self, article_bs):
        urls_bs = article_bs.find_all('a', class_="new__thumb")
        begin_link = "https://k1news.ru/news/"
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

            soup = BeautifulSoup(response.text, 'lxml')
            article_urls = self._extract_url(soup)
            for article_url in article_urls:
                self.urls.append(article_url)

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

    def _fill_article_with_text(self, article_bs):
        texts_bs = article_bs.find('div', class_='article__body')
        paragraphs_bs = texts_bs.find_all('p', class_=None)
        self.article.text = ''
        for paragraph_bs in paragraphs_bs:
            self.article.text += paragraph_bs.text

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        return self.article

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path (base_path)

    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(parents=True, exist_ok=True)

def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)
    max_articles = config["total_articles_to_find_and_parse"]
    seed_urls = config["seed_urls"]

    if not seed_urls:
        raise IncorrectURLError
    if not isinstance (seed_urls, list):
        raise IncorrectURLError
    for article_url in seed_urls:
        correct_url = re.match(r'https://', article_url)
        if not correct_url:
            raise IncorrectURLError

    if not isinstance (max_articles, int):
        raise IncorrectNumberOfArticlesError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    seed_links, maximum_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_links, max_articles=maximum_articles)
    crawler.find_articles()
    for i, url in enumerate (crawler.urls):
        parser = HTMLParser(url, i + 1)
        article = parser.parse()
        article.save_raw()
