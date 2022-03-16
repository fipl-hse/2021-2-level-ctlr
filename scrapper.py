"""
Scrapper implementation
"""
import datetime
import json
from pathlib import Path
import re
import shutil

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile
from constants import HEADERS, ASSETS_PATH


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

    def __init__(self, seed_urls, total_max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.urls = []

    @staticmethod
    def _change_the_link(link):
        if 'http://journals.tsu.ru' not in link:
            link = 'http://journals.tsu.ru' + link
        return link

    def _extract_url(self, article_bs):
        urls_bs = article_bs.find('div', class_='two_thirds')
        urls_bs = urls_bs.find_all('a')
        urls_bs_full = [self._change_the_link(url_bs['href']) for url_bs in urls_bs]
        return urls_bs_full

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)

            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, 'lxml')

            articles_urls = self._extract_url(soup)
            for full_url in articles_urls:
                if len(self.urls) < self.total_max_articles:
                    self.urls.append(full_url)

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

        # title
        title_bs = article_bs.find_all('h1')[-1]
        self.article.title = title_bs.text

        # author
        table_with_authors = article_bs.find('table', class_='content_table otvet_list')
        author_list_bs = table_with_authors.find_all('tr')[1]
        self.article.author = author_list_bs.find('td').text

        # topics
        header2_bs = article_bs.find('h2')
        topics_bs = header2_bs.find_next_siblings('a')
        self.article.topics = [topic.text for topic in topics_bs]

        # date
        big_title = article_bs.find('h1')
        pattern_of_date = r'\d{4}'
        result = re.findall(pattern_of_date, big_title.text)
        date_year = int(result[0])
        self.article.date = datetime.date(date_year, 1, 1)

    def _fill_article_with_text(self, article_bs):
        article_urls_bs = article_bs.find('a', class_='file pdf')
        pdf = PDFRawFile(article_urls_bs['href'], self.article_id)
        pdf.download()

        self.article.text = pdf.get_text()
        self.article.save_raw()

    def parse(self):
        response = requests.get(url=self.article_url, headers=HEADERS)

        with open(f'{ASSETS_PATH}/{self.article_id}_article_url.html', 'w', encoding='utf-8') as file:
            file.write(response.text)

        with open(f'{ASSETS_PATH}/{self.article_id}_article_url.html', encoding='utf-8') as file:
            response = file.read()

        article_bs = BeautifulSoup(response, 'lxml')

        self._fill_article_with_meta_information(article_bs)
        self._fill_article_with_text(article_bs)


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if Path(base_path).exists():
        shutil.rmtree(base_path)
    Path(base_path).mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    seed_urls = configuration["seed_urls"]
    total_articles_to_find_and_parse = configuration["total_articles_to_find_and_parse"]
    http_pattern = re.compile(r'^https?://')
    if not seed_urls:
        raise IncorrectURLError
    for url in seed_urls:
        result = http_pattern.search(url)
        if not result:
            raise IncorrectURLError
    if not isinstance(total_articles_to_find_and_parse, int):
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    pass
