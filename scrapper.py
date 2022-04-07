"""
Scrapper implementation
"""
import datetime
import json
import random
import re
import shutil
from collections import namedtuple
from dataclasses import dataclass, asdict
from pathlib import Path
from time import sleep
from typing import List

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from constants import HEADERS, CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile


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
    Total number of articles to parse is not integer  # in|is !typo
    """


class IncorrectNumberOfMaxArticlesFromSeedError(Exception):
    """
    Maximum number of articles to parse from one seed is not integer
    """


class BadStatusCode(Exception):
    """
    Request did not give valid response
    """


class Crawler:
    """
    Crawler implementation
    """

    def __init__(self, seed_urls: List[str], max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    def _extract_url(self, article_bs):
        contents_bs = article_bs.select('div.content-cont-col-text a')
        links = ['https://alp.iling.spb.ru/' + content['href'][2:] for content in contents_bs][:max_per_seed]
        self.urls.extend(links)

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            page = obtain_page(url)
            soup = BeautifulSoup(page, 'lxml')
            self._extract_url(soup)
            sleep(random.uniform(2, 4))
            return self.urls[:self.total_max_articles]

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


@dataclass
class Author:
    """
    Stores detailed information about article authors
    """
    name: str = 'NOT FOUND'
    organisation: str = 'NOT FOUND'
    email: str = 'NOT FOUND'


class HTMLParser:
    """
    Parser implementation
    """

    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        pdf_url = 'https://alp.iling.spb.ru/' + article_bs.select_one('div.article-download-r a')['href'][5:]
        pdf_file = PDFRawFile(pdf_url, self.article_id)
        pdf_file.download()
        self.article.text = pdf_file.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.select_one('h1.article-h1').text

        author_names = [name.text for name in article_bs.select('span.author-name')]
        author_organisations = [organisation.text for organisation
                                in article_bs.select('div.author-st')]
        author_emails = [email.text for email in article_bs.select('div.author-info-r a')]

        authors = [asdict(Author(name=person, organisation=org, email=mailbox)) for person, org, mailbox
                   in zip(author_names, author_organisations, author_emails)]

        self.article.author = authors

        date_raw = re.search(r'\d{4}', article_bs.select_one('div.article-text').text).group()
        article_date = datetime.datetime.strptime(date_raw, '%Y')
        self.article.date = article_date

        self.article.topics = article_bs.select_one('div.kw-tags').text.replace('\n', ' ').split(', ')

    def parse(self):
        page = obtain_page(self.article_url)
        article_bs = BeautifulSoup(page, 'lxml')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def obtain_page(url):
    """
    Reaches seed url and returns its content
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.encoding = 'UTF-8'
        return response.text
    except RequestException:
        return None


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    shutil.rmtree(base_path, ignore_errors=True)
    Path(base_path).mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    n_articles = config.get('total_articles_to_find_and_parse')
    is_n_articles = isinstance(n_articles, int) and n_articles > 0
    is_n_in_range = is_n_articles and n_articles < 1000

    seed_urls = config.get("seed_urls")
    pattern = re.compile(r'https://alp\.iling\.spb\.ru/issues/.+')
    is_seed_urls = seed_urls and all(pattern.match(str(seed)) for seed in seed_urls)

    max_n_from_seed = config.get("max_number_articles_to_get_from_one_seed")
    is_max_n = isinstance(max_n_from_seed, int)

    Validation = namedtuple('Validation', ['success', 'error'])
    validations = (
        Validation(is_n_articles, IncorrectNumberOfArticlesError),
        Validation(is_n_in_range, NumberOfArticlesOutOfRangeError),
        Validation(is_seed_urls, IncorrectURLError),
        Validation(is_max_n, IncorrectNumberOfMaxArticlesFromSeedError)
    )

    for test in validations:
        if not test.success:
            raise test.error()

    return seed_urls, n_articles, is_max_n


if __name__ == '__main__':
    start_urls, max_n_articles, max_per_seed = validate_config(CRAWLER_CONFIG_PATH)

    crawler = Crawler(
        seed_urls=start_urls,
        max_articles=max_n_articles,
        max_articles_per_seed=max_per_seed
    )

    prepare_environment(ASSETS_PATH)

    articles_found = crawler.find_articles()

    for index, article_link in enumerate(articles_found, start=1):
        parser = HTMLParser(article_url=article_link, article_id=index)
        article_instance = parser.parse()
        article_instance.save_raw()

        sleep(random.uniform(2, 4))
