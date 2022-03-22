"""
Scrapper implementation
"""
from datetime import datetime
import json
from pathlib import Path
import re
import shutil

from bs4 import BeautifulSoup
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         '(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}


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
        content_bs = article_bs.find_all('div', class_="issueArticle flex")
        for tag in content_bs:
            if len(self.urls) >= self.max_articles:
                break
            link = tag.find('a')
            main_link = link['href']
            self.urls.append(main_link)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(seed_url, HEADERS)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.is_dir():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as config:
        scrapper_config = json.load(config)

    seed_urls = scrapper_config["seed_urls"]
    max_articles = scrapper_config["total_articles_to_find_and_parse"]

    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    if not seed_urls:
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not re.match('https://', seed_url):
            raise IncorrectURLError

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 300:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


class HTMLParser:
    """
    Parser implementation
    """

    def __init__(self, article_url, article_id):
        """
        Init
        """
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)

    def parse(self):
        """
        Parses each article
        """
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):

        table_rows = article_bs.find('div', class_="fulltext")
        link = table_rows.find('a')['href']
        new_link = re.sub(r'(?i)view(?=\W)', 'download', link)
        pdf_file = PDFRawFile(new_link, self.article_id)

        pdf_file.download()
        self.article.text = pdf_file.get_text()

    def _fill_article_with_meta_information(self, article_bs):

        author_bs = article_bs.find('meta', {"name": "DC.Creator.PersonalName"})["content"]
        if not article_bs:
            article_bs = 'NOT FOUND'
        self.article.author = author_bs

        title_bs = article_bs.find('meta', {"name": "description"})['content']
        self.article.title = title_bs

        date_raw = article_bs.find("meta", {"name": "DC.Date.dateSubmitted"})['content']
        article_date = datetime.datetime.strptime(date_raw, '%Y-%m-%d')
        self.article.date = article_date


if __name__ == '__main__':

    seed_urls_test, total_articles_test = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seed_urls_test, total_articles_test)
    crawler.find_articles()

    ID = 0
    for url in crawler.urls:
        ID += 1
        article_parser = HTMLParser(article_url=url, article_id=ID)
        article = article_parser.parse()
        article.save_raw()
        print(f'The {ID} article is done!')
