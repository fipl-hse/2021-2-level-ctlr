"""
Generates config with flexible params for testing purposes
"""

import shutil
import json
from config.test_params import TEST_PATH, TEST_CRAWLER_CONFIG_PATH


def generate_config(seed_urls: list, num_articles: int, path: str = TEST_CRAWLER_CONFIG_PATH):
    config = dict()
    config['seed_urls'] = seed_urls
    config['total_articles_to_find_and_parse'] = num_articles

    if TEST_CRAWLER_CONFIG_PATH.exists():
        shutil.rmtree(TEST_PATH)
    TEST_PATH.mkdir(parents=True, exist_ok=True)
    with TEST_CRAWLER_CONFIG_PATH.open("w", encoding='utf-8') as f:
        json.dump(config, f)
