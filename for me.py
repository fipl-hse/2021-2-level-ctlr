from pymystem3 import Mystem

from pipeline import MorphologicalToken

# mystem = Mystem()
# text = Mystem().analyze('Мама мыла, раму а я, ел кириешки')
# tokens = []
# for word in text:
#     if not word.get('analysis'):
#         continue
#     morph_token = MorphologicalToken(original_word=word.get('text'))
#     morph_token.normalized_form = word.get('analysis')[0].get('lex')
#     morph_token.mystem_tags = word.get('analysis')[0].get('gr')
#     tokens.append(morph_token)
# for token in tokens:
#     print(token)
#     print(token.get_single_tagged())

tokens = ['ab', 'bb', 'masha']


def hallo(text, name):
    print(f'{text} is {name}')

text = ''
for i in tokens:
    text += i
hallo(" ".join(tokens), name='egor')
