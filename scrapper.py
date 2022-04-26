"""
Scrapper implementation
"""

import json
from pathlib import Path
import random
import re
import shutil
import time

from bs4 import BeautifulSoup
import requests

from constants import (
    ASSETS_PATH,
    CRAWLER_CONFIG_PATH,
    HEADERS
)
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
        for node in article_bs.find_all("a", {"class": "file"}):
            # ignore links to issues, only collect articles.
            # this does not leave out any content, because issues
            # are comprised of the same articles.
            if "issue" in node["href"]:
                continue
            if len(self.urls) == self.max_articles:
                break
            self.urls.append(node["href"])

    def find_articles(self):
        """
        Finds articles
        """
        for seed in self.seed_urls:
            if len(self.urls) == self.max_articles:
                break
            time.sleep(random.random())
            response = requests.get(seed, headers=HEADERS)
            article_bs = BeautifulSoup(response.text, features="html.parser")
            self._extract_url(article_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(url=article_url, article_id=article_id)

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, "html.parser")
        self._fill_article_with_text()
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self):
        pdf_url = self.article_url.replace("view", "download")
        print(pdf_url)
        time.sleep(random.random())
        pdf_raw = PDFRawFile(pdf_url, self.article_id)
        pdf_raw.download()
        self.article.text = pdf_raw.get_text()

    def _fill_text_with_meta_information(self, article_bs):
        pass

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    assets = Path(base_path)
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True)


def validate_config(crawler_path: Path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    if "seed_urls" not in config:
        raise IncorrectURLError
    if "total_articles_to_find_and_parse" not in config:
        raise IncorrectNumberOfArticlesError

    seed_urls = config["seed_urls"]
    max_articles = config["total_articles_to_find_and_parse"]

    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError
    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not _is_valid_url(seed_url):
            raise IncorrectURLError

    return seed_urls, max_articles


def _is_valid_url(url_to_validate):
    return re.match(r"https?://", url_to_validate)


if __name__ == '__main__':
    # YOUR CODE HERE
    seeds, limit = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seeds,
                      max_articles=limit)
    crawler.find_articles()

    for index, url in enumerate(crawler.urls):
        parser = HTMLParser(article_url=url,
                            article_id=index+1)
        article = parser.parse()
        article.save_raw()
