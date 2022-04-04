"""
Scrapper implementation
"""
from datetime import datetime
import json
from pathlib import Path
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HTTP_PATTERN


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
        # list with urls to articles
        self.urls = []

    def _extract_url(self, article_bs):
        all_urls_bs = article_bs.find_all('dd')
        urls_to_articles = []
        for url_bs in all_urls_bs:
            not_full_url = url_bs.find('a')['href']
            urls_to_articles.append(HTTP_PATTERN + not_full_url)

        for url_to_article in urls_to_articles:
            if len(self.urls) < self.total_max_articles:
                self.urls.append(url_to_article)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 5))
            response = requests.get(url=seed_url)
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_meta_information(self, article_bs):
        # DATE
        # the second date - of publication
        date_of_publication = article_bs.find_all('span', class_='date')[1].text
        time_of_publication = article_bs.find_all('span', class_='time')[1].text
        full_date = f'{date_of_publication} {time_of_publication}'
        self.article.date = datetime.strptime(full_date, '%d.%m.%Y %H:%M')

        # AUTHOR
        try:
            self.article.author = article_bs.find('em').text.strip()
        except AttributeError:
            self.article.author = 'NOT FOUND'
        # TOPICS
        self.article.topics = 'NOT FOUND'

        # TITLE
        self.article.title = article_bs.find('h1', class_="htitle black article--title").text.strip()

    def _fill_article_with_text(self, article_bs):
        # only text of the article
        self.article.text = article_bs.find('div', class_='news_detail_content').text.strip()

    def parse(self):
        sleep(random.randint(1, 5))
        response = requests.get(url=self.article_url)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    # path to folder
    path_for_environment = Path(base_path)

    if path_for_environment.exists():
        shutil.rmtree(path_for_environment)
    path_for_environment.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        scrapper_config = json.load(file)

    for url in scrapper_config["seed_urls"]:
        if HTTP_PATTERN not in url:
            print(url)
            raise IncorrectURLError

    seed_urls = scrapper_config["seed_urls"]
    total_articles_to_find_and_parse = scrapper_config["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(total_articles_to_find_and_parse, int) or total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    config_seed_urls, config_total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(config_seed_urls, config_total_articles)
    crawler.find_articles()

    COUNTER = 1
    for crawler_url in crawler.urls:
        article_parser = HTMLParser(article_url=crawler_url, article_id=COUNTER)
        article = article_parser.parse()
        article.save_raw()
        COUNTER += 1
