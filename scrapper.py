"""
Scrapper implementation
"""
import json
import re
import shutil
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from random import randint
from time import sleep
from datetime import datetime
from constants import ASSETS_PATH
from constants import CRAWLER_CONFIG_PATH
from constants import HEADERS
from constants import DOMAIN_NAME
from core_utils.article import Article


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
        articles = article_bs.find_all('div', class_='block-container')

        for article in articles:
            if len(self.urls) < self.max_articles:
                link = article.find('a')
                href = link['href']
                self.urls.append(href)

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(randint(1, 5))
            response = requests.get(seed_url, headers=HEADERS, allow_redirects=True)

            article_bs = BeautifulSoup(response.text, 'lxml')
            self.urls.extend(self._extract_url(article_bs))

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
        response = requests.get(self.article_url, headers=HEADERS, allow_redirects=True)

        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article

    def _fill_article_with_text(self, article_bs):
        """
        Fills the Article instance with text
        """
        text_bs = article_bs.find(class_="text-article").text
        self.article.text = text_bs.text

    def _fill_article_with_meta_information(self, article_bs):
        """
        Fills the Article instance with meta information
        """
        title_bs = article_bs.find(class_='top_big_img_article__info__inside__title').text
        self.article.title = title_bs
        print(title_bs)

        date_bs = article_bs.find(class_="top_big_img_article__info__inside__time").text
        date = datetime.strptime(date_bs, "%d.%m.%Y, %H:%M")
        self.article.date = date

        tags_bs = article_bs.find('div', class_='hash_tags')
        self.article.tags = tags_bs

        try:
            author_bs = article_bs.find(class_='top_big_img_article__info__inside__author').text
        except AttributeError:
            author_bs = 'NOT FOUND'
        self.article.author = author_bs

    def prepare_environment(base_path):
        """
        Creates ASSETS_PATH folder if not created and removes existing folder
        """
        path = Path(base_path)
        if path.exists():
            shutil.rmtree(base_path)
        base_path.mkdir(exist_ok=True, parents=True)

    def validate_config(crawler_path):
        """
        Validates given config
        """
        with open(crawler_path) as file:
            config = json.load(file)  # load is for decoding

        seed_urls = config['seed_urls']
        max_articles = config['total_articles_to_find_and_parse']

        if not seed_urls:
            raise IncorrectURLError

        for url in seed_urls:
            if not re.match(r'https?://', url):
                raise IncorrectURLError

        if not isinstance(max_articles, int) or max_articles <= 0:
            raise IncorrectNumberOfArticlesError

        if max_articles > 100:
            raise NumberOfArticlesOutOfRangeError

        crawler_path.prepare_environment(ASSETS_PATH)
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
