"""
Scrapper implementation
"""

import json
import re
import shutil
import pathlib
from time import sleep
import random
import requests
from bs4 import BeautifulSoup

from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH, HTTP_PATTERN
from core_utils.article import Article

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0."
                         "4692.71 Safari/537.36 Edg/97.0.1072.55", "Accept": "*/*"}
COOKIE = {"Cookie_1": "splituid=UET9A2IXrERz/AVMA3/0Ag==; __rmid=WxrRsu9SSViVssjG_hh9lA; _ym_d=1646042187; rbc_newsfeed"
                      "_toggle=1; rbc-newsfeed-time=1647540489996; toprbc_chooser=true; livetv-state=off; livetv-autopl"
                      "ay=145; mp_bfff2bb96fef5e2da8ecf6978c5306d5_mixpanel=%7B%22distinct_id%22%3A%20%2217fa2a7264e209"
                      "-07d96fd38f0ddf-34681542-1fa400-17fa2a7264fd71%22%2C%22%24device_id%22%3A%20%2217fa2a7264e209-07"
                      "d96fd38f0ddf-34681542-1fa400-17fa2a7264fd71%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2"
                      "Fnn.rbc.ru%2F%22%2C%22%24initial_referring_domain%22%3A%20%22nn.rbc.ru%22%7D; toprbc_date=Sat%20"
                      "Mar%2019%202022%2000%3A00%3A00%20GMT%2B0300%20(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D1%81%"
                      "D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5%20%D0%B2%D1%80%D0%B5%D0%BC%D1%8F); t"
                      "oprbc_region=world; js_d=false; __rfabu=0; __rmsid=Zg9xgRYKStyVQhevxjv1kg; qrator_msid=164996432"
                      "9.954.gkQbaJAJmfsdHSym-qvsgtl0g8nl7pfb44ikroqqcaohcj1fb",
          "Cookie_2": "yandexuid=2195954881537180309; mda=0; fuid01=5b9f82973a6fb3f2.noNNqtmOJVNzzDj-JQq7XnQ9NoRM-TRKqW"
                      "lXkoyartSQs2CELwAWgxtsVNj9ZnH4yvDzk8x7poK-hpdAkCgVNVxKOflmWZl-cxqxM0g_jsPoG89UMDGE3GtOqKRG1zrf; "
                      "my=YwA=; _ym_uid=1537198267522835919; yuidss=2195954881537180309; is_gdpr=0; is_gdpr_b=CKuXThDeB"
                      "igC; gdpr=0; amcuid=9360055691627476100; yandex_login=; yandex_gid=47; ymex=1963234913.yrts.1647"
                      "874913; VTouhmwR=1; FxuGQqNNo=1; computer=1; i=FFPSnLxLQb4WTOoAPdugmjhKUa6zGZUDyIr0pTPq9cCafi09S"
                      "+7Tn0PgGQA5VRkFiHV1/r0uA7NYMpebhGOansrEW+A=; sMLIIeQQeFnYt=1; yp=1942836515.multib.1#1680112592."
                      "p_sw.1648576591#1650441692.ygu.1#1650466915.spcs.l#1665568202.szm.1_25:1920x1080:1536x775#165239"
                      "5258.los.1#1652395258.losc.0#1650223564.clh.2233626#1650297705.mcv.0#1650297705.mct.null#1650308"
                      "865.zlgn_smrt.1; _ym_d=1649964365; yabs-sid=426183521649964364; _ym_isad=2; tCTmkfFoXn=1; yabs-f"
                      "requency=/5/00010000002n4EDW/LVTwO9j8Vb8OHY6qsqKWW2OCLnX68RMKMpnRSMDS64OZ8krF10oancuOHYFYtAkBN9b"
                      "iVXX6G2j_8LShdnDw64OW4sifM5S0000OHY05XSAJPRzFLnX6G5FgNBbbKZbz64PWODGzROO0000OHY0eRh1mbG0001b600N"
                      "v_79mb00001X689zoi700000064OW87roS000000OHa1pOIjk000001X6W000/; ys=mclid.2233626#wprid.164996440"
                      "7338579-14857827892382109792-sas6-5256-bb7-sas-l7-balancer-8080-BAL-8044"}


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
        self.urls = []

    def _extract_url(self, article_bs):
        urls_bs = article_bs.find_all('a', class_="item__link")
        all_urls = []

        for url_bs in urls_bs:
            last_part = url_bs['href']
            all_urls.append(f'{HTTP_PATTERN}{last_part}')
        return all_urls

    def find_articles(self):
        """
        Finds articles
        """
        for seed_url in self.seed_urls:
            sleep(random.randint(1, 10))
            response = requests.get(url=seed_url, headers=HEADERS, cookies=COOKIE)

            soup_lib = BeautifulSoup(response.text, 'lxml')

            urls = self._extract_url(soup_lib)
            for url in urls:
                if len(self.urls) < self.max_articles:
                    if url not in self.urls:
                        self.urls.append(url)

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

    def _fill_article_with_meta_information(self, article_bs):
        title_parent = article_bs.find('div', class_='article__header__title')
        title = title_parent.find('h1', class_='article__header__title-in js-slide-title').text  # print the title
        self.article.title = title.strip()   # delete spaces

        author_parent = article_bs.find('a', class_='article__authors__author')
        if author_parent in article_bs:
            author = author_parent.find('span', class_='article__authors__author__name')
            self.article.author = author.text
        else:
            self.article.author = 'NOT FOUND'

        self.article.date = 'NOT FOUND'
        self.article.topics = 'NOT FOUND'

    def _fill_article_with_text(self, article_bs):
        self.article.text = ''
        block_1 = article_bs.find('div', class_='article__text article__text_free')
        txt_group1 = block_1.find_all('p')
        txt_group1 = txt_group1.select_one('a').decompose()
        for i in txt_group1:
            self.article.text += i.text

        block_2 = article_bs.find('div', class_='article__text')
        txt_group2 = block_2.find_all('p')
        txt_group2 = txt_group2.select_one('a').decompose()  # delete irrelevant tag
        for k in txt_group2:
            self.article.text += k.text

    def parse(self):
        response = requests.get(self.article_url, headers=HEADERS, cookies=COOKIE)
        article_bs = BeautifulSoup(response.text, 'lxml')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)

        return self.article


def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    path = pathlib.Path(base_path)

    if path.exists():
        shutil.rmtree(base_path)
    path.mkdir(parents=True, exist_ok=True)


def validate_config(crawler_path):
    """
    Validates given config
    """
    with open(crawler_path) as file:
        config = json.load(file)

    seed_urls = config['seed_urls']
    total_articles = config['total_articles_to_find_and_parse']

    if not seed_urls:
        raise IncorrectURLError
    for article_url in seed_urls:
        correct_url = re.match(r'https://', article_url)
        if not correct_url:
            raise IncorrectURLError

    if not isinstance(total_articles, int):
        raise IncorrectNumberOfArticlesError

    if total_articles <= 0:
        raise IncorrectNumberOfArticlesError

    if total_articles > 200:
        raise NumberOfArticlesOutOfRangeError

    return seed_urls, total_articles


if __name__ == '__main__':
    seed_links, mx_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls=seed_links, max_articles=mx_articles)
    crawler.find_articles()

    for index, a_text in enumerate(crawler.urls):
        parser = HTMLParser(a_text, index + 1)
        article = parser.parse()
        article.save_raw()
