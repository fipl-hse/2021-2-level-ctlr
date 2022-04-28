"""
Scrapper implementation
"""

from datetime import datetime
import json
import random
import re
import shutil
import time

from bs4 import BeautifulSoup
import requests

from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH, HEADERS, URL_BEGINNING
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
            extracted_urls.append(URL_BEGINNING + link.get('href'))
        return extracted_urls

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            response = requests.get(url=seed_url, headers=HEADERS)
            time.sleep(random.randint(1, 3))
            if not response.ok:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            extracted_urls = self._extract_url(soup)
            for extracted_url in extracted_urls:
                if len(self.urls) == self.max_articles:
                    break
                self.urls.append(extracted_url)
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
        article_bs = BeautifulSoup(response.text, "html.parser")

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article

    def _fill_article_with_text(self, article_bs):
        page = article_bs.find("div", {"id": "main"})
        attachment = page.find("div", {"class": "attachmentsContainer"})
        pdf_link = URL_BEGINNING + attachment.find("a", {"class": "at_url"})["href"]

        pdf = PDFRawFile(pdf_link, self.article_id)
        pdf.download()

        pdf_text = pdf.get_text()
        if 'СПИСОК ЛИТЕРАТУРЫ' in pdf_text:
            split_pdf = pdf_text.split('СПИСОК ЛИТЕРАТУРЫ')
            self.article.text = split_pdf[0]
        else:
            self.article.text = pdf_text

    def _fill_article_with_meta_information(self, article_bs):
        self._fill_article_with_date(article_bs)
        page = article_bs.find("div", {"id": "main"})
        title_and_author = page.find('h2')
        title_and_author = title_and_author.text.replace(' "', "").replace('" ', "")

        title_and_author_list = title_and_author.split(".")
        title = title_and_author_list.pop(-1)
        self.article.title = title.strip()

        author = ".".join(title_and_author_list)
        if "," in author:
            self.article.author = author.split(",")[0].strip()
        else:
            self.article.author = author.strip()

        blocks = page.find_all("p", {"style": "text-align: justify;"})
        topics_prob = ""
        for block in blocks:
            if "Ключевые слова:" in block.text:
                topics_prob += block.text
        if "\xa0" not in topics_prob:
            topics = topics_prob.replace("Ключевые слова:", "")
            topics_list = topics.split(",")
            for topic in topics_list:
                if "." in topic:
                    self.article.topics.append(topic.replace(".", "").strip())
                else:
                    self.article.topics.append(topic.strip())

    def _fill_article_with_date(self, article_bs):
        page = article_bs.find("div", {"id": "main"})
        doi = page.find_all("p", {"style": "text-align: justify;"})[0]
        citation = page.find_all("p", {"style": "text-align: justify;"})[-1]
        date_of_article = ""

        year_prob = re.search(r'\.\d{4}\.', doi.text)
        if year_prob is None:
            year = re.search(r' \d{4}\.', citation.text).group(0)
        else:
            year = year_prob.group(0)
        for symbol in year:
            if symbol.isdigit():
                date_of_article += symbol

        day_and_month = {"1": "-01-01", "2": "-01-03", "3": "-01-05",
                         "4": "-01-07", "5": "-01-09", "6": "-01-11"}
        number_of_journal_prob = re.search(r'\.\d{4}\.\d', doi.text)
        if number_of_journal_prob is None:
            number_of_journal = re.search(r'№ \d', citation.text).group(0)[-1]
        else:
            number_of_journal = number_of_journal_prob.group(0)[-1]
        if number_of_journal in day_and_month.keys():
            date_of_article += day_and_month[number_of_journal]

        self.article.date = datetime.strptime(date_of_article, '%Y-%d-%m')


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir(exist_ok=True, parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    if "seed_urls" not in config.keys():
        raise IncorrectURLError
    seed_urls = config["seed_urls"]
    if "total_articles_to_find_and_parse" not in config.keys():
        raise IncorrectURLError
    number_of_articles = config["total_articles_to_find_and_parse"]
    if not seed_urls or not isinstance(seed_urls, list):
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError
        norm_url = re.match(URL_BEGINNING, seed_url)
        if not norm_url:
            raise IncorrectURLError
    if not isinstance(number_of_articles, int) or number_of_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if number_of_articles > 1:
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
        time.sleep(random.randint(1, 3))
        my_article = parser.parse()
        my_article.save_raw()
