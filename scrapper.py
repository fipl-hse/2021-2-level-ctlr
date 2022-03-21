"""
Scrapper implementation
"""
import datetime
import json
import pathlib
import re
import shutil

from bs4 import BeautifulSoup
import requests

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, DOMAIN_NAME
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

        """
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article

    def _fill_article_with_text(self, article_bs):
        """
        Fills self.article with text from article_bs
        """

        table_rows = article_bs.find_all('tr', {"class": "unnrow"})

        for table_row in table_rows:
            table_datas = table_row.find_all('td')

            if not table_datas:
                continue

            if "Загрузить статью" in table_datas[0].text:
                pdf_url = table_datas[1].find('a')

                pdf_raw_file = PDFRawFile(pdf_url['href'], self.article_id)

                pdf_raw_file.download()
                text = pdf_raw_file.get_text()

                parts_of_article = text.split('Список литературы')

                self.article.text = ''.join(parts_of_article[:-1])
                break

    def _fill_article_with_meta_information(self, article_bs):
        """
        Fills self.article with meta information
        """

        self.article.title = article_bs.find('h3').get_text()

        tables_bs = article_bs.find_all('table', {"class": "unntable"})

        for table_bs in tables_bs:
            table_datas_bs = table_bs.find_all('td')

            if table_datas_bs[0].text != 'Авторы':
                continue

            link_to_author_bs = table_datas_bs[1].find('a')

            self.article.author = link_to_author_bs.text

        text_date = re.search(r'Поступила в редакцию\s+\d{2}\.\d{2}\.\d{4}', self.article.text)

        if text_date:
            date_re = re.search(r'\d{2}\.\d{2}\.\d{4}', text_date.group(0))

            self.article.date = datetime.datetime.strptime(date_re.group(0), '%d.%m.%Y')


class Crawler:
    """
    Crawler implementation
    """
    def __init__(self, seed_urls, max_articles: int):
        self._seed_urls = seed_urls
        self.max_articles = max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        """
        Finds urls from the given article_bs
        """
        table_rows_bs = article_bs.find_all('tr', {"class": "unnrow"})

        urls = []
        overall_urls_count = len(self.urls)

        links_bs = []

        for table_row_bs in table_rows_bs:
            links_bs.extend(table_row_bs.find_all('a'))

        for link_bs in links_bs:
            if overall_urls_count > self.max_articles:
                break

            # Checks if the link leads to an article
            match = re.match(r'^\?anum', link_bs['href'])

            if not match:
                continue

            urls.append(''.join([DOMAIN_NAME, link_bs['href']]))
            overall_urls_count += 1

        return urls

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self._seed_urls:
            if len(self.urls) + 1 > self.max_articles:
                break

            response = requests.get(seed_url)
            article_bs = BeautifulSoup(response.text, features="html.parser")

            self.urls.extend(self._extract_url(article_bs))

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self._seed_urls


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = pathlib.Path(base_path)

    if path.exists():
        shutil.rmtree(path)

    path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r') as crawler_file:
        crawler_config = json.load(crawler_file)

    if 'total_articles_to_find_and_parse' not in crawler_config:
        raise IncorrectNumberOfArticlesError

    if 'seed_urls' not in crawler_config:
        raise IncorrectURLError

    max_articles = crawler_config['total_articles_to_find_and_parse']

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError

    seed_urls = crawler_config['seed_urls']

    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError

    for seed_url in seed_urls:
        match = re.match(r'(^http://|^https://)', seed_url)

        if not match or DOMAIN_NAME not in seed_url:
            raise IncorrectURLError

    prepare_environment(ASSETS_PATH)

    return seed_urls, max_articles


if __name__ == '__main__':
    outer_seed_urls, outer_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    crawler = Crawler(outer_seed_urls, outer_max_articles)
    crawler.find_articles()

    for i, url in enumerate(crawler.urls):
        parser = HTMLParser(url, i + 1)
        article = parser.parse()
        article.save_raw()
