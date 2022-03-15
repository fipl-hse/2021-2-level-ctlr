"""
Scrapper implementation
"""
import os, json, requests
from constants import ASSETS_PATH, CRAWLER_CONFIG_PATH
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
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
        class_bs = article_bs.find_all('div', class_= 'title')
        for title in class_bs:
            self.urls.append(title.find('a')['href'])

    def find_articles(self):
        """
        Finds articles
        """
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        useragent_random = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        headers = {
            'user-Agent': useragent_random.get_random_user_agent(),
            'accept': '*/*', 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': 'yandexuid=378107381599902934; yuidss=378107381599902934; yabs-sid=77084811599902934; _ym_uid=1599999416687409591; mda=0; yandex_login=Lamba.san.ves; is_gdpr=0; is_gdpr_b=CIecPxCgCCgC; ymex=1946826689.yrts.1631466689; i=2qKOpp0zgPBNSDoDCJiNrbXokGItqy4PgraK6tsDBOdas2KbnfHX9YlbmbqtITRh9B3+Gpoo0CB/ED19gC0v6EWW5yo=; my=YycCAAEA; ys=udn.cDpBenpydWdl#c_chck.2557583304; engineering=1; adequate=1; Session_id=3:1647183118.5.0.1600707115417:L3zQUg:7a.1.2:1|165114763.0.2|3:249379.414541.dtAgEpshCbhT1OCLh-rZpRjkeyc; sessionid2=3:1647183118.5.0.1600707115417:L3zQUg:7a.1.2:1|165114763.0.2|3:249379.414541.dtAgEpshCbhT1OCLh-rZpRjkeyc; yandex_gid=47; _ym_d=1647346782; _ym_isad=1; engineer=1; yabs-frequency=/5/1m0004ALic400000/_tpvefXTkLUWHI4Se3zjXW000A158N0_GMs60000e4KX5Hn1ROO0002OHIE2OK5jXW0009X58zbmYRSKiv9De4KW7SvxfH5gytrVHVp___zZIlIyL2gUUA15GDgIfCn34kfoe4MWWFeWDc9_qrQWHI1Zu8-izch6QQ1589NZTDXB_tbCe4KWbqyobYOQBagWHM0qPUZmFLzFGQ1588WF772I0000e4L0-n8SS980002XHG01-rImS9K0002XHQ01iniSS980002WHI3kTx1mbG000A15u0LKi72L0000e4M0Kt2mS9K0002WHI1GSB1mbG000A15O0Xqi72L0000e4L0/; yp=1916067115.udn.cDpBenpydWdl#1663114786.szm.1_25:1536x864:1382x642#1672264872.p_sw.1640728872#1678882784.ygu.1#1647692282.spcs.d#1649861531.csc.2'
        }
        for urls in self.seed_urls:
            response = requests.get(urls, headers=headers, allow_redirects=True)
            response.encoding = 'utf-8'
            with open('index2.html', 'w', encoding='utf-16') as file:
                file.write(response.text)
            #print(response.status_code)
            article_bs = BeautifulSoup(response.text, features='html.parser')
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

    def parse(self):
        response = requests.get(self.article_url)
        article_bs = BeautifulSoup(response.text, 'html.parser')

        self._fill_article_with_text(article_bs)
        self._fill_article_with_meta_information(article_bs)
        self.article.save_raw()

        return self.article

def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    try:
        os.rmdir(base_path)
    except FileNotFoundError:
        pass
    os.mkdir(base_path)


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
    if max_articles > 100:
        raise NumberOfArticlesOutOfRangeError
    for urls in seed_urls:
        if urls[0:8] != 'https://' and urls[0:7] != 'http://':
            raise IncorrectURLError
    return seed_urls, max_articles

if __name__ == '__main__':
    seed_urls, max_articles = validate_config(CRAWLER_CONFIG_PATH)
    prepare_environment(ASSETS_PATH)
    crawler = Crawler(seed_urls, max_articles)
    crawler.find_articles()
    print(crawler.urls)
  #  parser = ArticleParser(article_url=full_url, article_id=i)
