"""
Scrapper implementation
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, HEADERS


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
        main_block_bs = article_bs.find("div", {"class": "cat-children"})
        extracted_urls = []
        for link in main_block_bs.find_all("a"):
            if link == main_block_bs.find("li", {"class": "first"}).find("a"):
                continue
            extracted_urls.append('https://l.jvolsu.com/' + link.get('href'))
        return extracted_urls

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
            time.sleep(3)
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            extracted_urls = self._extract_url(soup)
            self.urls += extracted_urls
            if len(self.urls) >= self.max_articles:
                break
        return self.urls[:self.max_articles]

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

    def parse(self):
        response = requests.get(self.article_url, headers=HEADERS)
        time.sleep(3)
        article_bs = BeautifulSoup(response.text, "html.parser")

        self._fill_article_with_text(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        page = article_bs.find("div", {"id": "main"})
        attachment = page.find("div", {"class": "attachmentsContainer"})
        pdf_link = attachment.find("a", {"class": "at_url"})["href"]

        pdf = PDFRawFile(pdf_link, self.article_id)
        pdf.download()

        pdf_text = pdf.get_text()
        if 'Список литературы' in pdf_text:
            split_pdf = pdf_text.split('Список литературы')
            self.article.text = split_pdf[0]
        else:
            self.article.text = pdf.get_text()


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    directory = Path(base_path)
    for item in directory.iterdir():
        item.unlink()
    directory.rmdir()
    Path(directory).mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    seed_urls = config["seed_urls"]
    number_of_articles = config["total_articles_to_find_and_parse"]
    if not seed_urls or not isinstance(seed_urls, list):
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError
        norm_url = re.match(r"https?://", seed_url)
        if not norm_url:
            raise IncorrectURLError
    if not isinstance(number_of_articles, int) or number_of_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if number_of_articles > 50:
        raise NumberOfArticlesOutOfRangeError
    return seed_urls, number_of_articles


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
