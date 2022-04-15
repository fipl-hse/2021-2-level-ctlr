"""
Scrapper implementation
"""
from datetime import datetime
import json
from pathlib import Path
import random
import re
import shutil
from time import sleep

from bs4 import BeautifulSoup
import requests

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, DOMAIN
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

    def __init__(self, seed_urls, total_max_articles: int):
        self.seed_urls = seed_urls
        self.total_max_articles = total_max_articles
        self.urls = []

    def _extract_url(self, article_bs):
        article_summaries_bs = article_bs.find_all("div", class_="obj_article_summary")
        for article_summary_bs in article_summaries_bs:
            url_link = article_summary_bs.find('div', class_='title').find('a')['href']
            self.urls.append(url_link)

    def find_articles(self):
        """
        Finds articles
        """

        for url in self.seed_urls:
            response = requests.get(url)
            sleep_period = random.randint(1, 3)
            sleep(sleep_period)

            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        article_urls_bs = article_bs.find('a', class_='obj_galley_link pdf')
        if article_urls_bs is None:
            title_no_file = article_bs.find('h1', class_='page_title').text.strip()
            back_to_seed = article_bs.select_one('nav ol li:nth-child(3) a')['href']
            seed_bs = BeautifulSoup(requests.get(back_to_seed).text, 'lxml')
            sections = seed_bs.find_all("div", class_="obj_article_summary")
            for section in sections:
                if title_no_file in section.text:
                    found_article_url_bs = section.find('a', class_='obj_galley_link pdf')
                    if found_article_url_bs:
                        art_soup = BeautifulSoup(requests.get(found_article_url_bs['href']).text, 'lxml')
                        download_pdf = art_soup.find('a', class_='download')['href']
                        pdf = PDFRawFile(download_pdf, self.article_id)
                        pdf.download()
                        self.article.text = pdf.get_text().split('СПИСОК ЛИТЕРАТУРЫ')[0]
        if article_urls_bs is not None:
            response = requests.get(article_urls_bs['href'])
            soup = BeautifulSoup(response.text, 'lxml')
            url_download_pdf = soup.find('a', class_='download')['href']
        # file_type = response.headers['content-type']
        # if not file_type == 'application/msword':
            pdf = PDFRawFile(url_download_pdf, self.article_id)
            pdf.download()
            self.article.text = pdf.get_text().split('СПИСОК ЛИТЕРАТУРЫ')[0]

    def _fill_article_with_meta_information(self, article_bs):
        # title
        self.article.title = article_bs.find('h1', class_='page_title').text.strip()

        # author
        self.article.author = article_bs.find('ul', class_='item authors').find('li').find('span').text.strip()

        # topics
        self.article.topics = article_bs.find('div', class_='item keywords').find(
            'span', class_='value').text.strip().replace('\t', "").split(', ')

        # date
        try:
            date = article_bs.find('div', class_='item published').find('div', class_='value').text.strip()
            self.article.date = datetime.strptime(date, '%Y-%m-%d')
        except AttributeError:
            self.article.date = datetime.strptime('2021', '%Y')

    def parse(self):
        response = requests.get(url=self.article_url)

        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        if self.article.text:
            self._fill_article_with_meta_information(article_bs)
            return self.article
        return None


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """

    as_path = Path(base_path)
    if as_path.exists():
        shutil.rmtree(as_path)
    as_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    if "seed_urls" not in config:
        raise IncorrectURLError

    if "total_articles_to_find_and_parse" not in config:
        raise IncorrectNumberOfArticlesError

    for seed_url in config["seed_urls"]:
        if not re.match(DOMAIN, seed_url):
            raise IncorrectURLError

    seed_urls = config["seed_urls"]
    total_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    if total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    return seed_urls, total_articles


def check_saved_number(tmp_path):
    if len([path for path in Path(tmp_path).iterdir() if path.is_file()]) == 300:
        return True
    return False


if __name__ == '__main__':
    new_seed_urls, new_total_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(new_seed_urls, new_total_articles)
    crawler.find_articles()
    ID_OF_ARTICLE = 1
    for art_url in crawler.urls:
        if not check_saved_number(ASSETS_PATH):
            parser = HTMLParser(article_url=art_url, article_id=ID_OF_ARTICLE)
            article = parser.parse()
            if article:
                article.save_raw()
                print(f'the {ID_OF_ARTICLE} article is successfully downloaded')
                ID_OF_ARTICLE += 1

    print("That's all!")
