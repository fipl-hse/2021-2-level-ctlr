"""
Scrapper implementation
"""
import datetime
import json
import pathlib
import re
import shutil

from bs4 import BeautifulSoup, Tag
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, HEADERS
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
        """
        Extract URL
        """
        sections_bs = article_bs.find('div', {'class': 'sections'})
        urls_bs = sections_bs.find_all('a')
        for url_bs in urls_bs:
            if len(self.urls) < self.max_articles:
                if re.fullmatch(r'.*https:\/\/languagejournal\.spbu\.ru\/'
                                r'article\/view\/[0-9]*\/?(?![0-9])', url_bs['href']):
                    if url_bs['href'] not in self.urls:
                        self.urls.append(url_bs['href'])

    def find_articles(self):
        """
        Finds articles
        """

        for seed_url in self.seed_urls:
            response = requests.get(seed_url, headers=HEADERS)
            if not response.ok:
                break

            article_bs = BeautifulSoup(response.text, 'lxml')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    """
    HTMLWithPDFParser implementation
    """

    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_text(self, article_bs):
        """
        Extract text
        """
        pdf_link = article_bs.find('a', {'class': 'obj_galley_link pdf'})['href']
        response_pdf = requests.get(pdf_link, HEADERS)
        pdf_bs = BeautifulSoup(response_pdf.text, 'lxml')
        download_pdf = pdf_bs.find('a', {'class': 'download'})['href']

        pdf = PDFRawFile(download_pdf, self.article_id)

        pdf.download()
        self.article.text = pdf.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        """
        Extract Meta information
        """
        try:
            article_author_bs = article_bs.find('span', {'class': 'name'})
        except AssertionError:
            article_authors_bs = article_bs.find('ul', {'class': 'item authors'})
            article_authors_list_bs = article_authors_bs.findall('span', {'class': 'name'})
            article_author_bs = ' '.join(article_authors_list_bs)
        if not article_author_bs:
            article_author_bs = 'Not Found'
        if isinstance(article_author_bs, Tag):
            self.article.author = article_author_bs.text.strip()
        else:
            self.article.author = article_author_bs.strip()

        article_title_bs = article_bs.find('h1', {'class': 'page_title'})
        self.article.title = article_title_bs.text.strip()

        date_raw_bs = article_bs.find('meta', {'name': 'DC.Date.dateSubmitted'})['content']
        article_date_bs = datetime.datetime.strptime(date_raw_bs, '%Y-%m-%d')
        self.article.date = article_date_bs

    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = pathlib.Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    if "total_articles_to_find_and_parse" not in config:
        raise IncorrectNumberOfArticlesError

    if "seed_urls" not in config:
        raise IncorrectURLError

    seed_urls = config["seed_urls"]

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not seed_urls:
        raise IncorrectURLError

    for seed_url in seed_urls:
        if not re.match(r'.*https:\/\/languagejournal\.spbu\.ru', seed_url):
            raise IncorrectURLError

    total_articles = config["total_articles_to_find_and_parse"]

    if not isinstance(total_articles, int) or total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles > 300:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    given_seed_urls, given_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(given_seed_urls, given_max_articles)
    crawler.find_articles()

    for i, url in enumerate(crawler.urls):
        parser = HTMLParser(url, i + 1)
        article = parser.parse()
        article.save_raw()
