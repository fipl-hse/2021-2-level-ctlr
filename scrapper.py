"""
Scrapper implementation
"""

from datetime import datetime
import json
from pathlib import Path
import re
import time

from bs4 import BeautifulSoup
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, HEADERS
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
        main_block_bs = article_bs.find("div", {"class": "cat-children"})
        extracted_urls = []
        for link in main_block_bs.find_all("a"):
            if link == main_block_bs.find("li", {"class": "first"}).find("a"):
                continue
            extracted_urls.append('https://l.jvolsu.com' + link.get('href'))
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
            for extracted_url in extracted_urls:
                self.urls.append(extracted_url)
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
        self._fill_article_with_meta_information(article_bs)
        self._fill_article_with_data(article_bs)

        return self.article

    def _fill_article_with_text(self, article_bs):
        page = article_bs.find("div", {"id": "main"})
        attachment = page.find("div", {"class": "attachmentsContainer"})
        pdf_link = "https://l.jvolsu.com" + attachment.find("a", {"class": "at_url"})["href"]

        pdf = PDFRawFile(pdf_link, self.article_id)
        pdf.download()

        pdf_text = pdf.get_text()
        if 'Список литературы' in pdf_text:
            split_pdf = pdf_text.split('Список литературы')
            self.article.text = split_pdf[0]
        else:
            self.article.text = pdf_text

    def _fill_article_with_meta_information(self, article_bs):
        page = article_bs.find("div", {"id": "main"})
        title_and_author = page.find('h2')
        title_and_author = title_and_author.text.replace(' "', "").replace('" ', "")

        title = ""
        for letter in title_and_author[::-1]:
            if letter == ".":
                if title_and_author[title_and_author.index(letter) - 1].isupper():
                    break
            title += letter
        self.article.title = title[::-1][1:-2]

        author = title_and_author.replace(title[::-1], "")
        if "," in author:
            self.article.author = author.split(",")[0][4:]
        else:
            self.article.author = author[4:]

    def _fill_article_with_data(self, article_bs):
        page = article_bs.find("div", {"id": "main"})
        # I don't have normal date information, so let's try to get it from citation
        citation = page.find_all("p", {"style": "text-align: justify;"})[-1]
        date_inf = citation.text.replace('"', "")

        date_of_article = ""

        year = re.search(r'\d{4}\.', date_inf).group(0)
        for symbol in year:
            if symbol.isdigit():
                date_of_article += symbol

        # Well... I have only the knowledge that this journal is being published six times a year
        day_and_month = {"1": "-01-01", "2": "-01-03", "3": "-01-05",
                         "4": "-01-07", "5": "-01-09", "6": "-01-11"}
        number_of_journal = re.search(r'№ \d', date_inf).group(0)
        for number, month in day_and_month.items():
            if number in number_of_journal:
                date_of_article += month

        self.article.date = datetime.strptime(date_of_article, '%Y-%d-%m')


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
    if number_of_articles > 100:
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
