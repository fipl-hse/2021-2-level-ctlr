"""
Scrapper implementation
"""
import datetime
import json
from pathlib import Path
import re
import random
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile
from constants import HEADERS, HTTP_PATTERN, ASSETS_PATH, CRAWLER_CONFIG_PATH, MONTHS_DICT


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
        if HTTP_PATTERN not in link:
            link = HTTP_PATTERN + link
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
            sleep(random.randint(1, 5))
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
        self.article.title = str(title_bs)[4:-5]

        # author
        table_with_authors = article_bs.find('table', class_='content_table otvet_list')
        author_list_bs = table_with_authors.find_all('tr')[1]
        self.article.author = author_list_bs.find('td').text

        # topics
        meta_info = article_bs.find_all('meta')
        self.article.topics = meta_info[2]['content'].split(', ')

        # date
        self._fill_article_with_date(article_bs)

    def _fill_article_with_date(self, article_bs):
        big_title = article_bs.find('h1')
        pattern_number_of_pub = re.compile(r'№ \d+')
        match_number_of_pub = pattern_number_of_pub.search(big_title.text)
        number_of_pub = match_number_of_pub.group(0).replace(' ', '')

        response = requests.get('http://journals.tsu.ru/philology/&journal_page=archive', headers=HEADERS)
        article_bs = BeautifulSoup(response.text, 'lxml')
        table = article_bs.find('table')
        rows = table.find_all('tr')
        months = rows[0].find_all('td')
        month_number = 0
        for row in rows:
            cells = row.find_all('td')
            for index, cell in enumerate(cells):
                if number_of_pub in cell.text and not month_number:
                    month_number = index
                    break
        month = MONTHS_DICT[months[month_number].text]

        pattern_of_date = re.compile(r'\d{4}')
        year = pattern_of_date.search(big_title.text).group(0)
        self.article.date = datetime.datetime.strptime(f'{year}.{month}', '%Y.%m')

    def _fill_article_with_text(self, article_bs):
        article_urls_bs = article_bs.find('a', class_='file pdf')
        pdf = PDFRawFile(article_urls_bs['href'], self.article_id)
        pdf.download()
        text = pdf.get_text()
        first_part = text.split('Литература')[0]
        article_text = ''.join(first_part)
        self.article.text = article_text

    def parse(self):
        response = requests.get(url=self.article_url, headers=HEADERS)

        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path_to_base_path = Path(base_path)
    if path_to_base_path.exists():
        shutil.rmtree(base_path)
    path_to_base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as json_file:
        config = json.load(json_file)

    if "seed_urls" not in config and "total_articles_to_find_and_pars":
        raise IncorrectURLError
    http_pattern = re.compile(HTTP_PATTERN)
    for url in config["seed_urls"]:
        result = http_pattern.search(url)
        if not result:
            raise IncorrectURLError

    seed_urls = config["seed_urls"]
    total_articles_to_find_and_parse = config["total_articles_to_find_and_parse"]

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(total_articles_to_find_and_parse, int):
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles_to_find_and_parse > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles_to_find_and_parse


if __name__ == '__main__':
    print('---Preparing environment---')
    prepare_environment(ASSETS_PATH)
    seed_urls_test, total_articles_test = validate_config(CRAWLER_CONFIG_PATH)

    print('---Creating a Crawler---')
    crawler = Crawler(seed_urls_test, total_articles_test)
    crawler.find_articles()

    print('---Parsing---')
    for id_of_article, article_url_test in enumerate(crawler.urls):
        article_parser = HTMLParser(article_url=article_url_test, article_id=id_of_article + 1)
        article = article_parser.parse()
        article.save_raw()
        print(f'The {id_of_article + 1} article is done!')

    print('---Done!---')
