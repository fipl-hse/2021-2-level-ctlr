"""
Scrapper implementation
"""
from datetime import datetime
import re
import json
from pathlib import Path
import random
import shutil
from time import sleep
import requests
import html2text
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
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
        urls_to_aritcle = article_bs.find_all(class_="_top-news__list-item")
        new = []
        for article in urls_to_aritcle:
            hrefs = [reg[13:-1] for reg in re.findall(r"""<h1><a href=['"][^'"]+['"]""", str(article))]
            # hrefs = hrefs.extend([reg[13:-1] for reg in re.findall(r"""<h4><a href=['"][^'"]+['"]""", str(article))])
            if hrefs:
                for href in hrefs:
                    self.urls.append("https://vz.ru" + href)

        return new

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 5))

            try:
                response = requests.get(url=seed_url)
            except requests.exceptions.ConnectionError:
                requests.status_code = "Connection refused"

            if not response.ok:
                continue
            #  print(seed_url)

            soup = BeautifulSoup(response.text, 'lxml')
            #  soup = BeautifulSoup(response.text, 'html.parser')
            #  with open("meta2.txt", "w") as file:
            #    file.write(str(soup))
            self._extract_url(soup)


    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.article_url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def _fill_article_with_meta_information(self, article_bs):
        self.article.title = article_bs.find('article')#.find_all('a')[0].contents[0]
        print(article_bs.find('article'))
        author = article_bs.find(class_="extra").contents
        author = re.findall(r"""Текст: [\w ]+[^,'"<]""", str(author))[0][7:]
        self.article.author = author
        self.article.date = datetime.today()

    def _fill_article_with_text(self, article_bs):
        text_bs = article_bs.find_all(class_='text')
        h2t = html2text.HTML2Text()
        h2t.ignore_links = True
        text_bs = h2t.handle(str(text_bs))
        self.article.text = text_bs

    def parse(self):
        sleep(0.4)
        try:
            response = requests.get(self.article_url)
            article_bs = BeautifulSoup(response.text, 'html.parser')
            with open("meta21.txt", "w") as file:
                file.write(str(article_bs))
            self._fill_article_with_text(article_bs)
            self._fill_article_with_meta_information(article_bs)
            self.article.save_raw()
        except requests.exceptions.ConnectionError:
            print("Connection refused", self.article_url)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = Path(base_path)
    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    max_articles = config['total_articles_to_find_and_parse']

    if not isinstance(seed_urls, list):
        raise IncorrectURLError

    if not isinstance(max_articles, int):
        raise IncorrectNumberOfArticlesError

    for url in seed_urls:
        correct_url = re.match(r'https://', url)
        if not correct_url:
            raise IncorrectURLError

    if max_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    if max_articles <= 0:
        raise IncorrectNumberOfArticlesError

    return seed_urls, max_articles


if __name__ == '__main__':
    print("env configuration...")
    my_seed_urls, my_max_articles = validate_config(CRAWLER_CONFIG_PATH)
    #  print(my_seed_urls, my_max_articles)
    #  print(ASSETS_PATH)
    prepare_environment(ASSETS_PATH)

    print("searching articles...")
    crawler = Crawler(my_seed_urls, my_max_articles)
    crawler.find_articles()

    print("parsing of pages")
    for i in range(len(crawler.urls)):
        parser = HTMLParser(article_url=crawler.urls[i], article_id=i)
        article_a = parser.parse()
        #  print(article.author, article.date, article.title)
        #  print(article.text)
