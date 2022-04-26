"""
Scrapper implementation
"""
from datetime import datetime
import json
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
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

    def __init__(self, seed_urls, total_max_articles):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        article_topics = article_bs.find_all('a', class_='listing-preview__content')
        for element in article_topics:
            url = element['href']
            if len(self.urls) < self.total_max_articles and url not in self.urls:
                self.urls.append(url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 5))
            response = requests.get(url=seed_url, timeout=60)
            if not response.ok:
                continue
            article_bs = BeautifulSoup(response.text, 'lxml')
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
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_meta_information(self, article_bs):
        # заголовок
        self.article.title = article_bs.find('h1').text.strip()
        # автор
        try:
            self.article.author = article_bs.find('li', class_='article__authors-data-item').text.strip().split('  ')[0]
        except AttributeError:
            self.article.author = 'NOT FOUND'
        # ключевые слова
        self.article.topics.append(article_bs.find('span', class_='meta__text').text)
        # дата
        raw_date = article_bs.find('span', class_='meta__item meta__item_first-line').find('time')['datetime'][:-5]
        self.article.date = datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S')

    def _fill_article_with_text(self, article_bs):
        self.article.text = ''
        texts_bs = article_bs.find('div', class_='article__body')
        list_with_texts = texts_bs.find_all('p')
        for text_bs in list_with_texts:
            self.article.text += text_bs.text

    def parse(self):
        response = requests.get(url=self.article_url, timeout=60)
        article_bs = BeautifulSoup(response.text, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration_dict = json.load(file)
    if not isinstance(configuration_dict["seed_urls"], list):
        raise IncorrectURLError
    for url in configuration_dict["seed_urls"]:
        if 'https://www.mk.ru' not in url:
            raise IncorrectURLError
    seed_urls = configuration_dict["seed_urls"]
    total_articles_to_find_and_parse = configuration_dict["total_articles_to_find_and_parse"]
    if not seed_urls:
        raise IncorrectURLError
    if not isinstance(total_articles_to_find_and_parse, int):
        raise IncorrectNumberOfArticlesError
    if total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError
    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError
    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    main_seed_urls, main_total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(main_seed_urls, main_total_articles)
    crawler.find_articles()
    for i, crawler_url in enumerate(crawler.urls):
        article_parser = HTMLParser(article_url=crawler_url, article_id=i + 1)
        article = article_parser.parse()
        article.save_raw()
