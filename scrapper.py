"""
Scrapper implementation
"""
import json
import re
import shutil
import datetime
import requests
from bs4 import BeautifulSoup

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile

from constants import ASSETS_PATH
from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS
# for checks


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
        Extracts urls of articles
        """
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
    """
    Parser implementation
    """
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def parse(self):
        """
        Extracts all necessary data from the article web page
        """
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        """
        Fills the Article instance with text
        """
        fulltext = article_bs.find('div', {'class': 'fulltext'})
        page_link = fulltext.find('a')['href']  # link to a page with pdf

        response_pdf = requests.get(page_link, HEADERS)  # downloads page with pdf to find a link for download pdf
        pdf_bs = BeautifulSoup(response_pdf.text, 'html.parser')

        container = pdf_bs.find('div', id='pdfDownloadLinkContainer')
        download_link = container.find('a')['href']

        pdf = PDFRawFile(download_link, self.article_id)

        pdf.download()
        self.article.text = pdf.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        """
        Fills the Article instance with meta information
        """
        article_title = article_bs.find('div', id='articleTitle').find('h1')
        self.article.title = article_title.get_text()

        author = article_bs.find('meta', {'name': 'DC.Creator.PersonalName'})
        if not author:
            self.article.author = 'NOT FOUND'
        else:
            self.article.author = author['content']

        date_raw = article_bs.find('meta', {'name': 'DC.Date.dateSubmitted'})['content']
        date = datetime.datetime.strptime(date_raw, '%Y-%m-%d')
        self.article.date = date


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(exist_ok=True, parents=True)


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

    prepare_environment(ASSETS_PATH)
    return seed_urls, max_articles


if __name__ == '__main__':
    my_seed_urls, my_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(my_seed_urls, my_max_articles)
    crawler.find_articles()

    for i, my_url in enumerate(crawler.urls):
        parser = HTMLParser(my_url, i + 1)
        my_article = parser.parse()
        my_article.save_raw()
