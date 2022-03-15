"""
Scrapper implementation
"""
import json
import shutil
from pathlib import Path
import re
from bs4 import BeautifulSoup

from core_utils.article import Article
from core_utils.pdf_utils import PDFRawFile
import requests

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, PROJECT_ROOT


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


class ResponseIsNotOk(Exception):
    """
    Response status code is not ok
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
        pass

    def find_articles(self):
        """
        Finds articles
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,applicat '
                      'ion/signed-exchange;v=b3;q=0.9',
            'Acccept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        for index, url in enumerate(self.seed_urls):
            response = requests.get(url=url, headers=headers)

            if not response.ok:
                raise ResponseIsNotOk

            with open(f'{ASSETS_PATH}/{index}_url.html', 'w', encoding='utf-8') as file:
                file.write(response.text)

            with open(f'{ASSETS_PATH}/{index}_url.html', encoding='utf-8') as file:
                response = file.read()

            soup = BeautifulSoup(response, 'lxml')
            article = soup.find('a', class_='file pdf')
            self.urls.append(article['href'])

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        pass


class ArticleParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.pdf = PDFRawFile(article_url, article_id)
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        # just for code style
        art = article_bs

        self.article.text = self.pdf.get_text()
        self.article.save_raw()
        return None

    def parse(self):
        self.pdf.download()
        article_bs = BeautifulSoup()
        self._fill_article_with_text(article_bs)
        return


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
    total_articles = configuration["total_articles_to_find_and_parse"]
    http_pattern = re.compile(r'^https?://')
    for url in seed_urls:
        result = http_pattern.search(url)
        if not result:
            raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    prepare_environment(PROJECT_ROOT)
    validate_config(CRAWLER_CONFIG_PATH)
    # parser = ArticleParser(article_url=full_url, article_id=i)
