"""
Scrapper implementation
"""
import json
import random
import re
import shutil
from collections import namedtuple
from dataclasses import asdict
from pathlib import Path
from requests.exceptions import RequestException
from time import sleep
from typing import List

import requests
from bs4 import BeautifulSoup

from core_utils.article import Article, Author
from core_utils.pdf_utils import PDFRawFile
from constants import HEADERS, CRAWLER_CONFIG_PATH, ASSETS_PATH


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


class IncorrectNumberOfMaxArticlesFromSeedError:
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

    @staticmethod
    def _extract_url(article_bs):
        contents_bs = article_bs.select('div.content-cont-col-text a')
        links = [modify_link(content['href']) for content in contents_bs]
        return links

    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            page = obtain_page(url)
            soup = BeautifulSoup(page, 'lxml')
            articles = self._extract_url(soup)
            self.urls.extend(articles)
            sleep(random.uniform(2, 4))
            return self.urls[:self.total_max_articles]

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    """
    Parser implementation
    """

    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        pdf_url = modify_pdf_link(article_bs.select_one('div.article-download-r a')['href'])
        pdf_file = PDFRawFile(pdf_url, self.article_id)
        pdf_file.download()
        self.article.text = pdf_file.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = clean_string_data(article_bs.select_one('h1.article-h1').text)

        author_names = [clean_string_data(name.text) for name in article_bs.select('span.author-name')]
        author_organisations = [clean_string_data(organisation.text) for organisation
                                in article_bs.select('div.author-st')]
        author_emails = [email.text for email in article_bs.select('div.author-info-r a')]

        authors = [asdict(Author(name=person, organisation=org, email=mailbox)) for person, org, mailbox
                   in zip(author_names, author_organisations, author_emails)]

        self.article.authors = authors
        self.article.doi = article_bs.select_one('div.article-download-l').text[5:]
        self.article.keywords = re.split(pattern=r', |; ', string=clean_string_data(article_bs.select_one('div.kw-tags').text))
        self.article.reference = clean_string_data(article_bs.select_one('div.article-text').text)
        self.article.abstract = clean_string_data(article_bs.select_one('div.article-text p').text)
        self.article.literature = [clean_string_data(reference.text) for reference in article_bs.select('div.article-lit-disc')]

        # 8
        # TODO self.date = ... ADD YEAR WHEN IMPLEMENT RECURSIVE CRAWLER

        # TODO CONSIDER THAT THE RESOURCE IS HYBRID! (DIFFERENT BEHAVIOUR WHEN PARSING)
        #  MAY NOT BE PDF|MAY NOT BE META PAGE

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


def clean_string_data(data: str) -> str:
    """
    pass
    """
    if data:
        data = data.replace('\n', ' ')
    return data


def modify_link(link):
    """
    Makes absolute link from relative one
    """
    if 'https://alp.iling.spb.ru/' not in link:
        link = 'https://alp.iling.spb.ru/' + link[2:]
    return link


def modify_pdf_link(link):
    """
    Makes absolute link from relative one
    """
    if 'https://alp.iling.spb.ru/' not in link:
        link = 'https://alp.iling.spb.ru/' + link[5:]
    return link


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

        n_articles = config['total_articles_to_find_and_parse']
        is_n_articles = isinstance(n_articles, int)
        is_n_in_range = is_n_articles and 0 < n_articles < 1000

        seed_urls = config['seed_urls']
        pattern = re.compile(r'https://alp\.iling\.spb\.ru/issues/.+')
        is_seed_urls = all(pattern.match(str(seed)) for seed in seed_urls)

        max_n_from_seed = config["max_number_articles_to_get_from_one_seed"]
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
                raise test.error('Scrapper config check failed.')

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
