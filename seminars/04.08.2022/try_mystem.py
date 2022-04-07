from pathlib import Path

from pymystem3 import Mystem


def main():
    mystem = Mystem()
    plain_text_path = Path(__file__).parent / 'test.txt'

    with plain_text_path.open(encoding='utf-8') as f:
        plain_text = f.read()

    lemmatized_tokens = mystem.lemmatize(plain_text)

    print(type(lemmatized_tokens))  # list

    for token in lemmatized_tokens:
        print(token)

    print(f'Before: {plain_text}')
    print(f'After: {" ".join(lemmatized_tokens)}')


    # Task 1. Cleanup text from any punctuation marks

if __name__ == '__main__':
    main()
