"""
Scrapper implementation
"""
import datetime
import json
import random
import re
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

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
        self.urls = {}

    def _extract_url(self, scheme_bs):
        """
        Extracts articles
        """
        journals_urls = []
        content_bs = scheme_bs.find_all('div', class_="clearfix text-formatted")[1]
        links_bs = content_bs.find_all('li')
        for journal_link in links_bs:
            if len(journal_link) > 1:
                raw_journal_link = journal_link.find_all('a')[1]['href']
                if raw_journal_link[:len("//iling-ran.ru/web/news/")] == "//iling-ran.ru/web/news/":
                    journal_url = f"https:{raw_journal_link}"
                    journals_urls.append(journal_url)
        counter = 0
        for jrnl_url in journals_urls:
            response_jour = requests.get(url=jrnl_url, headers=HEADERS)
            article_bs_jour = BeautifulSoup(response_jour.text, 'lxml')
            content_bs_jour = article_bs_jour.find_all('div', class_="clearfix text-formatted")[1]
            links_bs_jour = content_bs_jour.find_all('li')
            for link in links_bs_jour:
                if link.find('a')['href'][-4:] == '.pdf':
                    if counter < self.max_articles:
                        if jrnl_url not in self.urls:
                            self.urls[jrnl_url] = [link]
                        else:
                            self.urls[jrnl_url].append(link)
                        counter += 1
                    else:
                        break

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
            sleep(random.randint(1, 5))

            scheme_bs = BeautifulSoup(response.text, 'lxml')
            self._extract_url(scheme_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class HTMLParser:
    """
    Parser implementation
    """
    def __init__(self, article_url, article_id, journal_url):
        self.journal_url = journal_url
        self.raw_article = article_url
        self.article_id = article_id
        self.article = Article(f'https:{article_url.find("a")["href"]}', self.article_id)

    def parse(self):
        """
        Extracts all necessary data from the article web page
        """
        self._fill_article_with_text(self.raw_article)
        self._fill_article_with_meta_information(self.raw_article)
        return self.article

    def _fill_article_with_text(self, article_bs):
        """
        Fills the Article instance with text
        """
        raw_download_page = article_bs.find('a')['href']
        download_page = f'https:{raw_download_page}'
        pdf_raw = PDFRawFile(download_page, self.article_id)
        pdf_raw.download()
        pdf_raw_text = pdf_raw.get_text()
        if 'литература' in pdf_raw_text:
            pdf_text = pdf_raw_text.split('литература')
            self.article.text = "".join(pdf_text[:-1])
        else:
            self.article.text = pdf_raw_text

    def _fill_article_with_meta_information(self, article_bs):
        """
        Fills the Article instance with meta information
        """
        article_title = article_bs.find('a').text
        self.article.title = article_title

        author_bald = article_bs.find('b')
        author_strong = article_bs.find('strong')

        if author_bald:
            self.article.author = author_bald.text
        elif author_strong:
            self.article.author = author_strong.text
        else:
            self.article.author = 'NOT FOUND'

        response_jour = requests.get(url=self.journal_url, headers=HEADERS)
        article_bs_jour = BeautifulSoup(response_jour.text, 'lxml')
        date_raw = article_bs_jour.find('span',
                                        class_="field field--name-created field--type-created field--label-hidden")
        date_raw = date_raw.text[4:]
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

    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, max_articles


if __name__ == '__main__':
    my_seed_urls, my_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(my_seed_urls, my_max_articles)
    crawler.find_articles()
    NUM_ARTICLE = 1
    for journal, articles in crawler.urls.items():
        for article in articles:
            parser = HTMLParser(article, NUM_ARTICLE, journal)
            my_article = parser.parse()
            my_article.save_raw()
            NUM_ARTICLE += 1
