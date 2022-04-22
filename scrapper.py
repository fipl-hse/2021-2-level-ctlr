"""
Scrapper implementation
"""
import datetime
import json
from pathlib import Path
import shutil

import requests
from bs4 import BeautifulSoup

from core_utils.article import Article
from constants import HEADERS, CRAWLER_CONFIG_PATH, ASSETS_PATH, HTTP_MAIN


class IncorrectURLError(Exception):
    """
    Seed URL does not match standard pattern
    """
    pass


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
        main_bs = article_bs.find('div', {'class': 'news-list-left'})
        links = main_bs.find_all('a', {'class': 'news-list-item'})
        for link in links:
            if len(self.urls) < self.max_articles:
                full_link = link['href']
                self.urls.append(HTTP_MAIN + full_link)


    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            self._extract_url(soup)



    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser():
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(self.article_url, self.article_id)

    def _fill_article_with_text(self, article_bs):
        whole_text = article_bs.find_all('div', {'class': 'text'})
        text = []
        for text_part in whole_text:
            text.append(text_part.text)
        self.article.text = '\n'.join(text)

    def _fill_article_with_meta_information(self, article_bs):
        article_title = article_bs.find('h2', {'class': 'news-title'})
        self.article.title = article_title.text

        self.article.author = 'NOT FOUND'

        date = '01/01/2022'
        compare_url = {}
        with open(CRAWLER_CONFIG_PATH) as file:
            config = json.load(file)
        config_seed_urls = config["seed_urls"]
        counter = 1
        response = config_seed_urls[0]
        for seed_url in config_seed_urls:
            compare_url[tuple(i for i in range(counter, counter+20))] = seed_url
            counter += 20
        for key in compare_url:
            if self.article_id in key:
                response = requests.get(url=compare_url.get(key), headers=HEADERS)
                break
        soup = BeautifulSoup(response.text, 'lxml')
        main_bs = soup.find('div', {'class': 'news-list-left'})
        links = main_bs.find_all('a', {'class': 'news-list-item'})
        for link in links:
            article_header = link.find('h3')
            if article_header is None:
                article_header = link.find('article')
            if article_title.text in article_header.text:
                date = link.find_all('time')[0].text + '/2022'
                break
        self.article.date = datetime.datetime.strptime(date, '%d/%m/%Y')

        self.article.topics = [topic for topic in article_bs.find('meta', {'name': 'keywords'})['content'].split(', ')]


    def parse(self):
        response = requests.get(self.article_url, HEADERS)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    config_seed_urls = config["seed_urls"]
    total_articles = config["total_articles_to_find_and_parse"]

    for seed_url in config_seed_urls:
        pattern = 'https://tomari.ru/news'
        if pattern not in seed_url:
            raise IncorrectURLError

    if not config_seed_urls:
        raise IncorrectURLError

    if not isinstance(config_seed_urls, list):
        raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles > 100:
        raise NumberOfArticlesOutOfRangeError

    return config_seed_urls, total_articles



if __name__ == '__main__':
    # YOUR CODE HERE
    seeds, articles_to_parse = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)

    crawler = Crawler(seeds, articles_to_parse)
    crawler.find_articles()

    for id_of_article, url in enumerate(crawler.urls):
        article_parser = HTMLParser(url, id_of_article + 1)
        article = article_parser.parse()
        article.save_raw()
