# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import unittest

from test_base import foss, TestFossologyUser, TestFossologyToken
from test_folders import TestFossologyFolders
from test_uploads import TestFossologyUploads
from test_jobs import TestFossologyJobs
from test_report import TestFossologyReport
from test_search import TestFossologySearch


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestFossologyToken("test_generate_token"))
    suite.addTest(TestFossologyUser("test_get_user"))
    suite.addTest(TestFossologyFolders("test_create_folder"))
    suite.addTest(TestFossologyFolders("test_update_folder"))
    suite.addTest(TestFossologyFolders("test_move_folder"))
    suite.addTest(TestFossologyFolders("test_delete_folder"))
    suite.addTest(TestFossologyUploads("test_upload_file"))
    suite.addTest(TestFossologyUploads("test_get_uploads"))
    suite.addTest(TestFossologyUploads("test_upload_from_vcs"))
    suite.addTest(TestFossologyUploads("test_upload_ignore_scm"))
    suite.addTest(TestFossologyUploads("test_upload_from_url"))
    suite.addTest(TestFossologyUploads("test_empty_upload"))
    suite.addTest(TestFossologyUploads("test_move_upload"))
    suite.addTest(TestFossologyJobs("test_schedule_jobs"))
    suite.addTest(TestFossologyUploads("test_upload_summary"))
    suite.addTest(TestFossologyUploads("test_upload_licenses"))
    suite.addTest(TestFossologyReport("test_generate_report"))
    suite.addTest(TestFossologySearch("test_search"))
    suite.addTest(TestFossologyUploads("test_delete_upload"))
    return suite


if __name__ == "__main__":

    runner = unittest.TextTestRunner()
    runner.run(suite())

    foss.close()
