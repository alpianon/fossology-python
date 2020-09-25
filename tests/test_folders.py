# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import time
import secrets
import unittest

from test_base import foss, logger
from fossology.obj import Folder
from fossology.exceptions import FossologyApiError, AuthorizationError


class TestFossologyFolders(unittest.TestCase):
    def test_create_folder(self):
        name = "FossPythonTest"
        desc = "Created via the Fossology Python API"
        # Create folder for unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.create_folder(foss.rootFolder, name, description=desc, group="test")
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

        test_folder = foss.create_folder(foss.rootFolder, name, description=desc)
        self.assertEqual(
            test_folder.name, name, f"Main test {name} folder couldn't be created"
        )
        self.assertEqual(
            test_folder.description,
            desc,
            "Description of folder on the server is wrong",
        )

        # Recreate folder to test API response 200
        test_folder = foss.create_folder(foss.rootFolder, name, description=desc)
        self.assertEqual(
            test_folder.name, name, f"Main test {name} folder couldn't be created"
        )

        # Create folder in arbitrary parent
        parent = Folder(secrets.randbelow(1000), "Parent", "", 0)
        self.assertRaises(AuthorizationError, foss.create_folder, parent, "No Parent")

        foss.delete_folder(test_folder)

    def test_update_folder(self):
        name = "FossPythonFolderUpdate"
        desc = "Created via the Fossology Python API"
        update_folder = foss.create_folder(foss.rootFolder, name, desc)

        name = "NewFolderName"
        desc = "Updated via the Fossology Python API"
        update_folder = foss.update_folder(update_folder, name=name, description=desc)
        self.assertEqual(update_folder.name, name, "Folder name couldn't be updated")
        self.assertEqual(
            update_folder.description, desc, "Folder description couldn't be updated"
        )
        foss.delete_folder(update_folder)

    def test_move_folder(self):
        move_copy_folder = foss.create_folder(
            foss.rootFolder, "MoveCopyTest", "Test move() and copy() functions"
        )
        test_folder = foss.create_folder(
            foss.rootFolder, "TestFolder", "Folder to be moved and copied via API"
        )
        try:
            test_folder = foss.move_folder(test_folder, move_copy_folder)
            self.assertEqual(
                test_folder.parent,
                move_copy_folder.id,
                "Folder was not moved to the expected location",
            )
        except FossologyApiError as error:
            logger.error(error.message)

        try:
            folder_copy = foss.copy_folder(test_folder, foss.rootFolder)
            folder_list = foss.list_folders()
            folder_copy = [
                folder
                for folder in folder_list
                if folder.parent == foss.rootFolder.id and folder.name == "TestFolder"
            ]
            self.assertIsNotNone(
                folder_copy, "Folder was not copied to the expected location"
            )
        except FossologyApiError as error:
            logger.error(error.message)
            return

        foss.delete_folder(move_copy_folder)
        foss.delete_folder(folder_copy[0])

    def test_delete_folder(self):
        folder = foss.create_folder(
            foss.rootFolder, "ToBeDeleted", "Test folder deletion via API"
        )
        foss.delete_folder(folder)
        time.sleep(3)
        try:
            deleted_folder = foss.detail_folder(folder)
            self.assertIsNotNone(deleted_folder, "Deleted folder still exists")
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":
    unittest.main()
    foss.close()
