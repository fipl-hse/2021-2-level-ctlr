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
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, PATTERN, HEADERS


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
        articles_block = article_bs.find('div', class_='b-news-inner__list')
        articles_bs_list = articles_block.find_all('div', class_='b-news-inner__list-item')
        for element in articles_bs_list:
            relative_url = element.find('a')['href']
            if relative_url[0] != '/' or not relative_url:
                continue
            full_url = PATTERN + relative_url
            if len(self.urls) < self.total_max_articles and full_url not in self.urls:
                self.urls.append(full_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(2, 4))
            response = requests.get(url=seed_url, headers=HEADERS)
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
        # title
        try:
            self.article.title = article_bs.find('h1', class_='b-material-head__title').text.strip()
        except AttributeError:
            self.article.title = article_bs.find('h1', class_='b-material-wrapper__title').text.strip()
        # author
        try:
            self.article.author = article_bs.find('a',
                                                  class_='b-link b-link_tag b-material-head__authors-link').text.strip()
        except AttributeError:
            self.article.author = 'NOT FOUND'
        # topics
        try:
            topics_block_bs = article_bs.find('div', class_='b-material-wrapper__rubric')
            topics_list_bs = topics_block_bs.find_all('a')
            for topic_bs in topics_list_bs:
                self.article.topics.append(topic_bs.text.strip())
        except AttributeError:
            self.article.topics = []
        # date
        try:
            raw_day = article_bs.find('span', class_='b-material-head__date-day').text
            raw_time = article_bs.find('span', class_='b-material-head__date-time').text
            raw_date = f'{raw_day} {raw_time}'
            self.article.date = datetime.strptime(raw_date, '%d.%m.%Y %H:%M')
        except AttributeError:
            self.article.date = datetime.strptime('', '')

    def _fill_article_with_text(self, article_bs):
        self.article.text = ''
        texts_bs = article_bs.find_all('p')
        for text_bs in texts_bs:
            add_text = text_bs.text
            self.article.text += add_text

    def parse(self):
        response = requests.get(url=self.article_url, timeout=20, headers=HEADERS)
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
        config = json.load(file)

    if not isinstance(config["seed_urls"], list):
        raise IncorrectURLError

    for url in config["seed_urls"]:
        if PATTERN not in url:
            raise IncorrectURLError

    seed_urls = config["seed_urls"]
    total_articles_to_find_and_parse = config["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(total_articles_to_find_and_parse, int) or total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    main_seed_urls, main_total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(main_seed_urls, main_total_articles)
    crawler.find_articles()

    for index, main_article_url in enumerate(crawler.urls):
        article_parser = HTMLParser(article_url=main_article_url, article_id=index + 1)
        article = article_parser.parse()
        article.save_raw()
