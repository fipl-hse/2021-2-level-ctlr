"""
Scrapper implementation
"""
import json
import re
import os
import requests
from bs4 import BeautifulSoup

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile

from constants import ASSETS_PATH
#from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS


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
        content = article_bs.find_all('div', {'class': 'issueArticle flex'})
        for article in content:
            link = article.find('a')
            href = link['href']
            self.urls.append(href)

    def find_articles(self):
        """
        Finds articles
        """

        for url in self.seed_urls:
            response = requests.get(url, HEADERS)  # get html code
            article_bs = BeautifulSoup(response.text, 'html.parser')  # creates BS object
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def parse(self):

        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()
        return self.article

    def _fill_article_with_text(self, article_bs):

        fulltext = article_bs.find('div', {'class': 'fulltext'})
        page_link = fulltext.find('a')['href']  # link to a page with pdf

        response_pdf = requests.get(page_link, HEADERS)  # downloads page with pdf to find a link for download pdf
        pdf_bs = BeautifulSoup(response_pdf.text, 'html.parser')

        container = pdf_bs.find('div', id='pdfDownloadLinkContainer')
        download_link = container.find('a')['href']

        print(download_link)

        pdf = PDFRawFile(download_link, self.article_id)

        pdf.download()
        self.article.text = pdf.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """

    try:
        os.rmdir(base_path)  # removes a folder
    except FileNotFoundError:
        os.mkdir(base_path)  # creates new one if it doesn't exist


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)  # load is for decoding

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    for url in seed_urls:
        if not re.match(r'https?://', url):  # https or http
            raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
