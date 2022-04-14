import pymorphy2


def main():
    morph_analyzer = pymorphy2.MorphAnalyzer()
    parsing_result = morph_analyzer.parse('стали')[0]
    print(parsing_result.tag)
    print(parsing_result.tag.POS)
    print(parsing_result.tag.cyr_repr)
    print(parsing_result.normal_form)
    print(parsing_result.normalized)


if __name__ == '__main__':
    main()
