"""
Scrapper implementation
"""
import json
import os
import pathlib
import shutil
import re
import datetime
import requests
from bs4 import BeautifulSoup
from constants import CRAWLER_CONFIG_PATH, ASSETS_PATH
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
        self.max_articles = max_articles
        self.seed_urls = seed_urls
        self.count_articles = 0
        self.urls = []

    def _extract_url(self, article_bs):  # I don't understand if I need to collect seed urls (from main to year)
        # or just put it in scrapper_config.
        articles_code_stored_here = article_bs.find_all('div', {'class': 'articles'})
        for article_code in articles_code_stored_here:
            links_articles = article_code.find_all('a')
            for link in links_articles:
                if self.max_articles == self.count_articles:
                    break
                try:
                    art_link = link["href"]
                    if art_link.startswith('/') and 'pdf' not in art_link:
                        self.urls.append('https://periodical.pstgu.ru' + link["href"])
                        self.count_articles += 1
                except KeyError:
                    continue

    def find_articles(self):
        """
        Finds articles
        """  # I also don't understand what I need to do here, because this code can be moved to extract_url
        for seed_url in self.seed_urls:
            issue_page = requests.get(seed_url)
            issue_page_bs = BeautifulSoup(issue_page.text, 'html.parser')
            self._extract_url(issue_page_bs)

    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls


class HTMLParser:
    def __init__(self, article_url, article_id):
        self.url = article_url
        self.article_id = article_id
        self.article = Article(article_url, article_id)

    def parse(self):
        article_page = requests.get(self.url)
        article_bs = BeautifulSoup(article_page.text, 'html.parser')
        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        return self.article

    def _fill_article_with_text(self, article_bs):
        list_of_possible_l = ['Список литературы', 'ЛИТЕРАТУРА', 'Список использованных источников и литературы',
                              'Источники']

        class_of_link = article_bs.find('div', {'class': "articles-item-more"})
        if class_of_link:
            link_to_save = class_of_link.find('a')
            link_to_pdf = 'https://periodical.pstgu.ru' + link_to_save['href']
            final_page = requests.get(link_to_pdf)
            final_page_bs = BeautifulSoup(final_page.text, 'html.parser')
        else:
            final_page_bs = article_bs
        url_pattern = re.compile(r"var DEFAULT_URL = '(.*?)'")
        final_link = final_page_bs.find(string=url_pattern)
        final_link = 'https://periodical.pstgu.ru' + \
                     str(final_link).replace('var DEFAULT_URL = ', '').replace("'", '').replace(';', '').strip()
        raw_pdf = PDFRawFile(final_link, self.article_id)
        raw_pdf.download()
        text_from_pdf = raw_pdf.get_text()
        for refs_maker in list_of_possible_l:
            if refs_maker in text_from_pdf:
                text_pdf_list = text_from_pdf.split(refs_maker)
                del text_pdf_list[-1]
                text_from_pdf = ' '.join(text_pdf_list)
        self.article.text = text_from_pdf

    def _fill_article_with_meta_information(self, article_bs):
        issue_number = []
        month_dict = {2: '03', 3: '06', 0: '09', 1: '12'}
        try:
            author = article_bs.find('p', {"class": "articles-item-author"}).find('b')
            self.article.author = author.text
        except AttributeError:
            self.article.author = 'No data'
        title = article_bs.find('h2', {"class": "articles-item-name"})
        self.article.title = title.text
        topics = article_bs.find('div', {"class": "articles"}).find_all('p')
        try:
            self.article.topics = topics[2].text
        except IndexError:
            self.article.topics = 'No data'
        year = article_bs.find('meta', {'name': 'citation_publication_date'})['content']
        issue_title = article_bs.find('meta', {'name': 'citation_journal_title'})['content']
        for letter in issue_title:
            if letter.isdigit():
                issue_number.append(letter)
        month = month_dict[int(''.join(issue_number)) % 4]
        text_date = month + '.' + year
        date = datetime.datetime.strptime(text_date, '%m.%Y')
        self.article.date = date


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    base_path_p = pathlib.Path(base_path)
    if os.path.exists(base_path_p):
        shutil.rmtree(base_path_p)
        base_path_p.mkdir(parents=True)
    else:
        base_path_p.mkdir(parents=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as path_thing_idk:
        config_dict = json.load(path_thing_idk)
    seed_urls = config_dict['seed_urls']
    max_articles = config_dict["total_articles_to_find_and_parse"]
    if not isinstance(max_articles, int) or max_articles <= 0:
        raise IncorrectNumberOfArticlesError
    if max_articles > 150:
        raise NumberOfArticlesOutOfRangeError
    if not isinstance(seed_urls, list):
        raise IncorrectURLError
    if len(seed_urls) <= 1:
        raise IncorrectURLError
    for seed_url in seed_urls:
        if not isinstance(seed_url, str):
            raise IncorrectURLError
        if not seed_url.startswith('https://'):
            raise IncorrectURLError

    return seed_urls, max_articles

if __name__ == '__main__':
    # YOUR CODE HERE
    i = 0
    s_urls, max_as = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(s_urls, max_as)
    crawler.find_articles()
    for art_url in crawler.urls:
        i += 1
        print(i)
        print(art_url)
        parser = HTMLParser(art_url, i)
        article = parser.parse()
        article.save_raw()
