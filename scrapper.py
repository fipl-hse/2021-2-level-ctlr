"""
Scrapper implementation
"""
import datetime
import json
import random
import re
import shutil
from time import sleep
import requests
from bs4 import BeautifulSoup

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
        Extracts articles
        """
        content_bs = article_bs.find_all('div', class_="clearfix text-formatted")[1]
        links_bs = content_bs.find_all('li')
        for journal_link in links_bs:
            if len(journal_link) > 1:
                raw_journal_url = journal_link.find_all('a')[1]['href']
                journal_pattern = "//iling-ran.ru/web/news/"
                if len(self.urls) < self.max_articles:
                    if raw_journal_url[:len(journal_pattern)] == journal_pattern:
                        journal_url = f"https:{raw_journal_url}"
                        if not journal_url in self.urls:
                            self.urls.append(journal_url)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
            sleep(random.randint(1, 5))

            article_bs = BeautifulSoup(response.text, 'lxml')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


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
        content_bs = article_bs.find_all('div', class_="clearfix text-formatted")[1]
        raw_download_page = content_bs.find_all('p')[1].find('a')['href']
        download_page = f'https:{raw_download_page}'
        pdf = PDFRawFile(download_page, self.article_id)
        pdf.download()
        self.article.text = pdf.get_text()

    def _fill_article_with_meta_information(self, article_bs):
        """
        Fills the Article instance with meta information
        """
        journal_title = article_bs.find('span',
                                        class_="field field--name-title field--type-string field--label-hidden")
        self.article.title = journal_title.text
        article_title = article_bs.find_all('div', class_="clearfix text-formatted")[1]
        links_bs = article_title.find_all('li')
        for link in links_bs:
            author_bald = link.find('b')
            author_strong = link.find('strong')

            if author_bald:
                self.article.author = author_bald.text
            elif author_strong:
                self.article.author = author_strong.text
            else:
                self.article.author = 'NOT FOUND'

            if link.find("a")["href"][-4:] == ".pdf":
                self.article.url = f'https:{link.find("a")["href"]}'
        date_raw = article_bs.find('span',
                                   class_="field field--name-created field--type-created field--label-hidden").text[4:]
        article_date = datetime.datetime.strptime(date_raw, '%d.%m.%Y - %H:%M')
        self.article.date = article_date


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
    with open(crawler_path) as file:
        config = json.load(file)

    http_pattern = re.compile(r"https://iling-ran.ru/web/ru/publications")
    for url in config['seed_urls']:
        if not re.match(http_pattern, url):
            raise IncorrectURLError

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 15:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    my_seed_urls, my_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(my_seed_urls, my_max_articles)
    crawler.find_articles()
    for i, my_url in enumerate(crawler.urls):
        parser = HTMLParser(my_url, i + 1)
        my_article = parser.parse()
        my_article.save_raw()
