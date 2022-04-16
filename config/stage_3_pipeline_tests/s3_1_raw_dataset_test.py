"""
Tests for validation dataset of raw texts
"""
import pathlib
import shutil
import unittest

import pytest

from constants import CRAWLER_CONFIG_PATH
from pipeline import EmptyDirectoryError, validate_dataset
from config.stage_2_crawler_tests.s2_1_crawler_config_test import (
                                                        ExtendedTestCase
                                                                    )


print("Stage 2A: Validating Assets Path")
print("Starting tests with received assets folder")


class PipelinePathCheck(ExtendedTestCase):
    """
    Tests for pipeline behavior relating different path input
    """
    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_1_dataset_sanity_checks
    def test_pipe_fails_if_path_not_exists(self):
        """
        Ensure that pipeline raises an error when given invalid path
        """
        not_existing_path = pathlib.Path("plain_text")

        error_message = "Checking that scrapper can handle " \
                        "not existing assets paths failed."
        self.assertRaisesWithMessage(error_message,
                                     FileNotFoundError,
                                     validate_dataset,
                                     not_existing_path)

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_1_dataset_sanity_checks
    def test_pipe_fails_if_no_files_in_folder_path(self):
        """
        Ensure that pipeline raises an error when given empty directory
        """
        test_dir = pathlib.Path('test_assets')

        test_dir.mkdir(parents=True, exist_ok=True)

        error_message = "Checking that empty directories " \
                        "can not be processed failed."
        self.assertRaisesWithMessage(error_message,
                                     EmptyDirectoryError,
                                     validate_dataset,
                                     test_dir)

        shutil.rmtree(test_dir)

    @pytest.mark.mark4
    @pytest.mark.mark6
    @pytest.mark.mark8
    @pytest.mark.mark10
    @pytest.mark.stage_3_1_dataset_sanity_checks
    def test_assets_path_not_directory(self):
        """
        Ensure that pipeline raises an error when given non-existing directory
        """
        error_message = "Checking that pipeline fails " \
                        "if given not a directory path."
        self.assertRaisesWithMessage(error_message,
                                     NotADirectoryError,
                                     validate_dataset,
                                     CRAWLER_CONFIG_PATH)


print("Done")

if __name__ == "__main__":
    unittest.main()
