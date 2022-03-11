"""
Checks raw dataset volume
"""

import os
import unittest

import pytest

from constants import ASSETS_PATH


class VolumeBasicCheckTest(unittest.TestCase):
    """
    Checks folder volume is appropriate
    """

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_4_dataset_volume_check
    def test_folder_is_appropriate(self):
        self.assertTrue(os.listdir(ASSETS_PATH),
                        msg="ASSETS_PATH directory is empty")


class VolumeCheckTest(unittest.TestCase):
    """
    Checks folder volume is appropriate
    """

    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_2_4_dataset_volume_check
    def test_folder_is_appropriate(self):
        metas, raws = 0, 0
        for file in os.listdir(ASSETS_PATH):
            if file.endswith("_raw.txt"):
                raws += 1
            if file.endswith("_meta.json"):
                metas += 1

        self.assertEqual(metas, raws,
                         msg="""Collected dataset do not contain equal number of raw_articles and metas""")
