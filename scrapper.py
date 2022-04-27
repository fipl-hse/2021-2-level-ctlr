"""
Crawler implementation
"""
import os
import json
import requests
import random
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
from article import Article
from constants import CRAWLER_CONFIG_PATH, HEADERS, ASSETS_PATH


class IncorrectURLError(Exception):
    """
    Custom error
    """


class NumberOfArticlesOutOfRangeError(Exception):
    """
    Custom error
    """


class IncorrectNumberOfArticlesError(Exception):
    """
    Custom error
    """


class UnknownConfigError(Exception):
    """
    Most general error
    """


class Crawler:
    """
    Crawler implementation

    """
    def __init__(self, seed_urls: list, max_articles: int, max_articles_per_seed: int):
        self.seed_urls = seed_urls
        self.total_max_articles = max_articles
        self.max_articles_per_seed = max_articles_per_seed
        self.urls = []

    @staticmethod
    def _extract_url(article_link):
        return 'https://www.psychologies.ru' + article_link

    def too_much_from_seed(self, articles_links_raw):
        if len(articles_links_raw) == max_num_per_seed or len(articles_links_raw) == max_num_articles:
            return True
        
     def find_articles(self): 
        """
        Finds articles

        Список статей на сайте https://www.psychologies.ru состоит из двух основных блоков: 
        "razdel-section" и "rubric-anons_list section-three-blocks".
        """
        for url in self.seed_urls:
            response = requests.get(url, headers=HEADERS)
            if not response:
                raise IncorrectURLError

            page_soup = BeautifulSoup(response.content, features='lxml')
            articles_links_raw = []
            if not self.too_much_from_seed(articles_links_raw):
                article_soup_razdels = page_soup.find_all('div', class_="razdel-section")
                for razdel in article_soup_razdels:
                    article_soups = razdel.find_all('div', class_='row-container rubric-anons')
                    for article_soup in article_soups:
                        articles_links_raw.append(article_soup.find('a', class_="rubric-anons_title")['href'])
                        if self.too_much_from_seed(articles_links_raw):
                            break
                    if self.too_much_from_seed(articles_links_raw): 
                        break
            if not self.too_much_from_seed(articles_links_raw):
                article_soup_rubrics = page_soup.find_all('div', class_="rubric-anons_list section-three-blocks")
                for rubric in article_soup_rubrics:
                    article_soups = rubric.find_all('div', class_='item grid_2')
                    for article_soup in article_soups:
                        articles_links_raw.append(article_soup.find('a', class_="link")['href'])
                        if self.too_much_from_seed(articles_links_raw):
                            break
                            if self.too_much_from_seed(articles_links_raw):
                                break

            for article_link in articles_links_raw: 
                seed_url = self._extract_url(article_link) 
                self.urls.append(seed_url) 
            
    def get_search_urls(self):
        """
        Returns seed_urls param
        """
        return self.seed_urls
    
    class ArticleParser: 
    """
    ArticleParser implementation
    """
    def __init__(self, full_url: str, article_id: int):
        self.full_url = full_url
        self.article_id = article_id
        self.article = Article(url=full_url, article_id=article_id)
        
        def _fill_article_with_text(self, article_soup):
            article_text = article_soup.find('section', itemprop='articleBody').find_all(['h2','h3','p'])
            for par in article_text:
                self.article.text += par.text.strip() + '\n' 

    def _fill_article_with_meta_information(self, article_soup):
        self.article.title = article_soup.find('h1', class_='article__title').text
        self.article.author = article_soup.find('div', itemprop="author").meta['content']
        artical_topics_raw = article_soup.find('div', class_='article').find('div', class_='themes mb-3')('a', class_='themes__theme')
        for artical_topic in artical_topics_raw:
            self.article.topics.append(artical_topic.text)
            article_date_raw = article_soup.find('meta', itemprop='datePublished')['content']
            self.article.date = self.unify_date_format(article_date_raw)
            
            @staticmethod
            def unify_date_format(date_str):
                """
                Unifies date format

        From    2022-04-22T11:48:45.453Z 
        or      2022-04-22T11:48:45Z

        To      2022-04-22 11:48:45
        """
        try:
            article_date_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                article_date_datetime = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                return article_date_datetime.strftime("%Y-%m-%d %H:%M:%S")
     def parse(self)     
        """
        Parses each article
        """
        response = requests.get(self.full_url, headers=HEADERS)
        if not response:
            raise IncorrectURLError
            
            article_soup = BeautifulSoup(response.text, 'lxml')
            self._fill_article_with_text(article_soup)
            self._fill_article_with_meta_information(article_soup)
            return self.article
        
    def prepare_environment(base_path):
    """
    Creates ASSETS_PATH folder if not created and removes existing folder
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
        
    def validate_config(crawler_path): 
    """
    Validates given config
    """
    try:
        with open(crawler_path, 'r', encoding='utf-8') as config:
            params = json.load(config)

        seed_urls = params.get('base_urls')
        max_articles = params.get('total_articles_to_find_and_parse')
        max_articles_per_seed = params.get('max_number_articles_to_get_from_one_seed')
        
        if not isinstance(seed_urls, list):
            raise IncorrectURLError
        for url in seed_urls:
            if not isinstance(url, str) or not url.startswith('http'):
                raise IncorrectURLError

        if not isinstance(max_articles, int) or max_articles < 0:
            raise IncorrectNumberOfArticlesError

        if not isinstance(max_articles_per_seed, int) or max_articles_per_seed > 100:
            raise NumberOfArticlesOutOfRangeError
            
    except(IncorrectURLError, IncorrectNumberOfArticlesError, NumberOfArticlesOutOfRangeError) as error:
        raise error
    else:
        return seed_urls, max_articles, max_articles_per_seed
    

if __name__ == '__main__': 
    # YOUR CODE HERE
    seed_urls_list, max_num_articles, max_num_per_seed = validate_config(CRAWLER_CONFIG_PATH) 
    crawler = Crawler(seed_urls=seed_urls_list,
                      max_articles=max_num_articles,
                      max_articles_per_seed=max_num_per_seed)
    crawler.find_articles() 
    prepare_environment(ASSETS_PATH) 
    for article_id_num, article_url in enumerate(crawler.urls, 1): 
        parser = ArticleParser(full_url=article_url, article_id=article_id_num)
        article = parser.parse()
        article.save_raw()
        sleep(random.randrange(5, 7)) 
