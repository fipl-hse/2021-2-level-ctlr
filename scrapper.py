"""
Scrapper implementation
"""
import json
import shutil
from datetime import datetime

import requests
import validators
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
        self.urls.append('http://www.elista.org' + article_bs.find('a')['href'])

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'user-agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'accept': '*/*'
        }
        for url in self.seed_urls:
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            page_bs = BeautifulSoup(response.text, features='html.parser')
            class_bs = page_bs.find_all('div', class_='grid_19 omega')
            for article_bs in class_bs:
                if len(self.urls) < self.max_articles:
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

    def _fill_article_with_text(self, article_bs):
        """
        fills article instance with text of article
        """
        text_bs = article_bs.find('div', class_='fullnews_content')
        self.article.text = text_bs.text

    def _fill_article_with_meta_information(self, article_bs):
        """
        fills article instance with title, date and topics
        """
        meta_bs = article_bs.find('div', class_='news_item fullnews')
        title_bs = meta_bs.find('h1').text
        self.article.title = title_bs

        topic = article_bs.find('h4', class_='chapter_h').text
        self.article.topics.append(topic)

        self.article.author = 'NOT FOUND'

    def _fill_article_with_date(self, article_bs):
        """
        fills article instance with title, date and topics
        """
        meta_bs = article_bs.find('div', class_='news_item fullnews')
        date_bs = meta_bs.find('span', class_='date').text
        date = datetime.strptime(date_bs, '%d.%m.%Y : %H.%M')
        self.article.date = date

    def parse(self):
        """
        does all the work. Working guy
        """
        headers = {
            'user-agent':
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'accept' : '*/*'
        }
        response = requests.get(self.article_url, headers=headers)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self._fill_article_with_date(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        shutil.rmtree(base_path)
    except FileNotFoundError:
        pass
    base_path.mkdir(parents=True)


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
        if not validators.url(urls):
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    sites, articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(sites, articles)
    crawler.find_articles()
    for article_url_new in crawler.urls:
        parsing_article = HTMLParser(article_url_new, crawler.urls.index(article_url_new)+1)
        parsed_article = parsing_article.parse()
        parsed_article.save_raw()
