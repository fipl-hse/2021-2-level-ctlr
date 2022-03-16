"""
Scrapper implementation
"""
import json
import os
import requests
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

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

    def _link_formatting(link):
        if 'https://www.kommersant.ru' not in link:
            link = 'https://www.kommersant.ru' + link
        return link

    def _extract_url(self, article_bs):
        urls_bs = article_bs.findall(class_="uho__link uho__link--overlay")
        urls_bs_full = [self._link_formatting(url_bs['href']) for url_bs in urls_bs]
        return urls_bs_full


    def find_articles(self):
        """
        Finds articles
        """
        for url in self.seed_urls:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br'
                'Accept-Language': 'en-US,en;q=0.5'
            }
            for seed_url_index, seed_url in enumerate(self.seed_urls):
                response = requests.get(url=seed_url)
            with open(f'{ASSETS_PATH}/{seed_url_index}_seed_url.html', 'w', encoding='utf-8') as file:
                file.write(response.text)
            with open(f'{ASSETS_PATH}/{seed_url_index}_seed_url.html', encoding='utf-8') as file:
                response = file.read()
            soup = BeautifulSoup(response.text, features="lxml")

            articles_urls_bs = self._extract_url(soup)
            list_of_urls = [url_bs for url_bs in articles_urls_bs if len(self.urls) < self.max_articles]
            for full_url in list_of_urls:
                if len(self.urls) <= self.max_articles:
                    self.urls.append(full_url)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir('ASSETS_PATH')
    except FileNotFoundError:
        pass
    os.mkdir('ASSETS_PATH')


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        configuration = json.load(file)

    seed_urls = configuration["seed_urls"]
    total_articles = configuration["total_articles_to_find_and_parse"]

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError
    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    # YOUR CODE HERE
    pass
