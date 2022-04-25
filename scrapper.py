"""
Scrapper implementation
"""

from datetime import datetime
import json
from pathlib import Path
import shutil


from bs4 import BeautifulSoup, element
import requests

from core_utils.article import Article
from constants import HEADERS, CRAWLER_CONFIG_PATH, ASSETS_PATH, HTTP_MAIN


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
        main_bs = article_bs.find('div', {'class': 'article-tile-news'})
        if main_bs is None:
            main_bs = article_bs.find('div', {'class': 'wrap preview-section__rows preview-section__rows_3'})
        for url_bs in main_bs:
            if len(self.urls) < self.max_articles:
                if isinstance(url_bs, element.NavigableString):
                    break
                link = url_bs.find('a')
                full_link = link['href']
                pattern_and_link = HTTP_MAIN + full_link
                if pattern_and_link not in self.urls:
                    self.urls.append(pattern_and_link)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
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

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find('div', {'class': 'article-detail__content'})
        if text_bs is not None:
            self.article.text = text_bs.text

    def _fill_article_with_meta_information(self, article_bs):
        date = article_bs.find('div', {'class': 'breadcrumbs__date'})
        if date is not None:
            date_test = date.text.strip()
            date_for_meta = datetime.strptime(date_test, "%d.%m.%Y, %H:%M")
            self.article.date = date_for_meta

        author = article_bs.find('div', {'class': 'author-wrapper article-detail__author'})
        author_name = author.find('span', {'field': 'name'})
        if not author_name:
            author_name = 'Not Found'
        self.article.author = author_name.text.strip()

        title = article_bs.find('h1', {'class': 'article-detail__title'})
        if title is not None:
            self.article.title = title.text

    def parse(self):
        response = requests.get(url=self.article_url, headers=HEADERS)
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
    path.mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)
    seed_urls = config['seed_urls']
    total_articles = config["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    for seed_url in seed_urls:
        pattern = 'https://esquire.ru/'
        if pattern not in seed_url:
            raise IncorrectURLError

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles > 180:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    given_seed_urls, given_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(given_seed_urls, given_max_articles)
    crawler.find_articles()

    for id_of_article, url in enumerate(crawler.urls):
        article_parser = HTMLParser(url, id_of_article + 1)
        article = article_parser.parse()
        article.save_raw()