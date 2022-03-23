"""
Scrapper implementation
"""
import json
import requests
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
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
        self.urls.append('https://magadanpravda.ru/' + article_bs.find('a')['href'])

    def find_articles(self):
        """
        Finds articles
        """
        for urls in self.seed_urls:
            response = requests.get(urls)
            response.encoding = 'utf-8'
            page_bs = BeautifulSoup(response.text, features='html.parser')
            class_bs = page_bs.find_all('h3', class_='el-title uk-h4 uk-margin-top uk-margin-remove-bottom')
            for article_bs in class_bs:
                if len(self.urls) < self.max_articles:
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
        self.article = Article(article_url, article_id)

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find('div', class_='el-content uk-panel uk-margin-top')
        self.article.text = text_bs.text

    def _fill_article_with_meta_information(self, article_bs):
        title_bs = article_bs.find('h2', class_='el-title uk-font-tertiary uk-margin-top uk-margin-remove-bottom').text
        self.article.title = title_bs

        date_bs = article_bs.find('div', class_='el-meta uk-text-meta uk-margin-top').text
        months = {
            'января':'01', 'февраля':'02', 'марта':'03', 'апреля':'04', 'мая':'05', 'июня':'06', 'июля':'07', 'августа':'08', 'сентября':'09', 'октября':'10', 'ноября':'11', 'декабря':'12',
        }
        for key, value in months.items():
            date_bs = date_bs.replace(key, value)
        date = datetime.strptime(date_bs, "%d %m %Y | %H:%M")
        self.article.date = date


        topic = article_bs.find_all('span', class_='uk-text-middle')
        for hashtags in topic:
            self.article.topics.append(hashtags.text)

        self.article.author = 'NOT FOUND'

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        shutil.rmtree(base_path)
    except FileNotFoundError:
        pass
    base_path.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']
    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if not isinstance(seed_urls, list) or not seed_urls:
        raise IncorrectURLError
    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError
    for urls in seed_urls:
        if urls[0:8] != 'https://' and urls[0:7] != 'http://':
            raise IncorrectURLError
    return seed_urls, max_articles


if __name__ == '__main__':
    sites, articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(sites, articles)
    crawler.find_articles()
    A_ID = 1
    for article_url_new in crawler.urls:
        parsing_article = HTMLParser(article_url_new, A_ID)
        parsed_article = parsing_article.parse()
        parsed_article.save_raw()
        A_ID += 1
