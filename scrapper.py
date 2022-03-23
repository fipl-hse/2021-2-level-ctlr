"""
Scrapper implementation
"""
from bs4 import BeautifulSoup
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
from core_utils.article import Article
from datetime import datetime
import json
from pathlib import Path
from random import randint
import re
import requests
import shutil
from time import sleep

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
        article_url_block = article_bs.find('div', id='_id_article_listing')
        urls_to_articles = article_url_block.find_all('a')
        new_urls = []
        for url_to_article in urls_to_articles:
            url = url_to_article['href']
            pattern = r'https://gazeta.ru'
            need_url = re.search(r'https://', url)
            if not need_url:
                new_urls.append(pattern + url)
            else:
                new_urls.append(url)
        return new_urls

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            sleep(randint(1, 5))
            response = requests.get(url)
            page_bs = BeautifulSoup(response.text, 'lxml')
            urls = self._extract_url(page_bs)
            for url in urls:
                if len(self.urls) < self.max_articles:
                    self.urls.append(url)

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
        text_bs = article_bs.find('div', class_='b_article-text')
        self.article.text = text_bs.text

    def _fill_article_with_meta_information(self, article_bs):
        title_bs = article_bs.find('h1', class_='headline').text
        self.article.title = str(title_bs)

        author_bs = article_bs.find('div', class_='author')
        if not author_bs.find('a'):
            self.article.author = 'NOT FOUND'
        else:
            self.article.author = author_bs.find('a').text

        self.article.topics = 'NOT FOUND'

        date_bs = article_bs.find('time').text
        months = {"января": "01", "февраля": "02", "марта": "03", "апреля": "04",
                  "мая": "05", "июня": "06", "июля": "07", "августа": "08",
                  "сентября": "09", "октября": "10", "ноября": "11",
                  "декабря": "12"}
        for month in months.keys():
            if month in date_bs:
                date_bs = date_bs.replace(month, months[month])
        self.article.date = datetime.strptime(date_bs, '\n%d %m %Y, %H:%M\n')

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']
    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError
    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    for url in seed_urls:
        correct_url = re.match(r'https://', url)
        if not correct_url:
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE

    my_seed_urls, my_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(my_seed_urls, my_max_articles)
    crawler.find_articles()
    for i, my_url in enumerate(crawler.urls):
        parser = HTMLParser(my_url, i+1)
        article = parser.parse()
        article.save_raw()