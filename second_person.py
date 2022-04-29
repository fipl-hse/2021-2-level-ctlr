import re

from pipeline import CorpusManager, validate_dataset
from constants import ASSETS_PATH, SECOND_PERSON_PATH
from improved_article import ArtifactType

if __name__ == "__main__":
    validate_dataset(ASSETS_PATH)
    corpus_manager = CorpusManager(ASSETS_PATH)
    matches = []
    for article in corpus_manager.get_articles().values():
        print(article.article_id)
        tagged = article.get_file(ArtifactType.single_tagged)
        for match in re.findall(r"([А-Яа-я]*)<V\S*(ед)\S*(2-л)\S*>", tagged):
            matches.append(match[0])
    with SECOND_PERSON_PATH.open("w", encoding="utf-8") as file:
        file.write(" ".join(matches))