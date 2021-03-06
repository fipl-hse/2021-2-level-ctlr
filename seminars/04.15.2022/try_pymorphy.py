import time
from pathlib import Path

import pymorphy2


def main():
    morph_analyzer = pymorphy2.MorphAnalyzer()
    all_parses = morph_analyzer.parse('стали')
    print(f'Analyzer found {len(all_parses)} different options of what this word means')

    # Usually we should take the first one - it is correct for most of cases
    parsing_result = morph_analyzer.parse('стали')[0]

    # Parsing result has a Tag object, to write it to file, it should be converted to string first of all
    print(parsing_result.tag)

    # Inspect Tag object as it has many important attributes
    print(parsing_result.tag.POS)

    # If you do not understand English terms of morphological analysis, use Russian translation
    print(parsing_result.tag.cyr_repr)

    # To get just a normal form, use an attribute `normal_form`
    print(parsing_result.normal_form)

    # To get full Parse object for a normal form use another property: `normalized`
    print(parsing_result.normalized)

    # news from https://www.nn.ru/text/education/2022/04/07/71171432/
    plain_text_path = Path(__file__).parent / 'test.txt'

    with plain_text_path.open(encoding='utf-8') as f:
        plain_text = f.read()

    all_words = plain_text.split()

    start = time.time()
    for word in all_words:
        print(f'{word}: {pymorphy2.MorphAnalyzer().parse(word)[0].tag}')
    many_instances_time = time.time() - start

    start = time.time()
    morph_analyzer = pymorphy2.MorphAnalyzer()
    for word in all_words:
        print(f'{word}: {morph_analyzer.parse(word)[0].tag}')
    single_instance_time = time.time() - start

    print(f'Time spent (seconds) for MorphAnalyzer instance per each word: {many_instances_time}')  # 4.3 sec
    print(f'Time spent (seconds) for MorphAnalyzer instance per each word: {single_instance_time}')  # 0.1 sec

    print(f'Single instance is quicker in {many_instances_time / single_instance_time: .2f}x')  # 41x

    # Very interesting to read: https://pymorphy2.readthedocs.io/en/stable/internals/dict.html#id13


if __name__ == '__main__':
    main()
