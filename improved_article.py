"""
Improved article implementation
"""

import json

from core_utils.article import ASSETS_PATH, Article, ArtifactType


class ImprovedArticle(Article):
    def get_file(self, kind=ArtifactType):
        with open(self.get_file_path(kind=kind), encoding="utf-8") as file:
            return file.read()

    def save_updated_meta(self, update_dict):
        updated_meta = self._get_meta() | update_dict
        with (ASSETS_PATH / self.get_meta_file_path()).open("w", encoding="utf-8") as file:
            json.dump(updated_meta, file, sort_keys=False,
                      indent=4, ensure_ascii=False, separators=(",", ": "))

    def get_image_path(self):
        return ASSETS_PATH / f"{self.article_id}_image.png"