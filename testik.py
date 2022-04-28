from pathlib import Path
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
import re

from constants import ASSETS_PATH
from core_utils.article import Article, ArtifactType
from pipeline import MorphologicalToken

# processed_text = Mystem().analyze('Я Егор Жариков и я ел рыбу каждый день')
# tokens = []
# pymorph_analyzer = MorphAnalyzer()
# for processed_word in processed_text:
#     if not processed_word.get('text') or not processed_word.get('analysis'):
#         continue
#     morph_token = MorphologicalToken(original_word=processed_word['text'])
#     morph_token.normalized_form = processed_word['analysis'][0]['lex']
#     morph_token.tags_mystem = processed_word['analysis'][0]['gr']
#     morph_token.tags_pymorphy = pymorph_analyzer.parse(processed_word['text'])[0].tag
#     tokens.append(morph_token)
# for token in tokens:
#     print(token.get_single_tagged())
if ASSETS_PATH.stat().st_size != 0:
    print('a')


