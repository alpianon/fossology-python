# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
import pytest
import responses

from fossology import Fossology
from fossology.obj import AccessLevel, Folder, Upload, SearchTypes
from fossology.exceptions import AuthorizationError, FossologyApiError


def test_upload_sha1(upload: Upload):
    assert upload.uploadname == "base-files_11.tar.xz"
    assert upload.filesha1 == "D4D663FC2877084362FB2297337BE05684869B00"
    assert (
        f"Upload '{upload.uploadname}' ({upload.id}, {upload.filesize}B, {upload.filesha1}) "
        f"in folder {upload.foldername} ({upload.folderid})"
    ) in str(upload)


def test_detail_upload_nogroup(foss: Fossology, upload: Upload, test_file_path: str):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.detail_upload(upload.id, group="test")
    assert (
        f"Getting details for upload {upload.id} for group test not authorized"
        in str(excinfo.value)
    )


@responses.activate
def test_detail_upload_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(
        responses.GET, f"{foss_server}/api/v1/uploads/{upload.id}", status=404
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_upload(upload.id)
    assert f"Error while getting details for upload {upload.id}" in str(excinfo.value)


def test_upload_nogroup(foss: Fossology, upload_folder: Folder, test_file_path: str):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_file(
            upload_folder,
            file=test_file_path,
            description="Test upload from github repository via python lib",
            group="test",
        )
    assert (
        f"Upload of {test_file_path} for group test in folder {upload_folder.id} not authorized"
        in str(excinfo.value)
    )


@responses.activate
def test_upload_error(
    foss_server: str, foss: Fossology, test_file_path: str, upload_folder: Folder
):
    upload_description = "Test upload from github repository via python lib"
    responses.add(
        responses.POST, f"{foss_server}/api/v1/uploads", status=404,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_file(
            upload_folder, file=test_file_path, description=upload_description,
        )
    assert f"Upload {upload_description} could not be performed" in str(excinfo.value)


@responses.activate
def test_get_uploads_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(responses.GET, f"{foss_server}/api/v1/uploads", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_uploads()
    assert "Unable to retrieve the list of uploads" in str(excinfo.value)


def test_get_uploads_nogroup(foss: Fossology):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.list_uploads(group="test")
    assert "Retrieving list of uploads for group test not authorized" in str(
        excinfo.value
    )


def test_get_uploads(foss: Fossology, upload_folder: Folder, test_file_path: str):
    name = "FossPythonTestUploadsSubfolder"
    desc = "Created via the Fossology Python API"
    upload_subfolder = foss.create_folder(upload_folder, name, description=desc)
    foss.upload_file(
        upload_folder,
        file=test_file_path,
        description="Test upload from github repository via python lib",
    )
    foss.upload_file(
        upload_subfolder,
        file=test_file_path,
        description="Test upload from github repository via python lib",
    )
    assert len(foss.list_uploads(folder=upload_folder)) == 2
    assert len(foss.list_uploads(folder=upload_folder, recursive=False)) == 1
    assert len(foss.list_uploads(folder=upload_subfolder)) == 1


def test_upload_from_vcs(foss: Fossology):
    vcs = {
        "vcsType": "git",
        "vcsUrl": "https://github.com/fossology/fossology-python",
        "vcsName": "fossology-python-github-master",
        "vcsUsername": "",
        "vcsPassword": "",
    }
    vcs_upload = foss.upload_file(
        foss.rootFolder,
        vcs=vcs,
        description="Test upload from github repository via python lib",
        access_level=AccessLevel.PUBLIC,
    )
    assert vcs_upload.uploadname == vcs["vcsName"]
    assert not foss.search(searchType=SearchTypes.DIRECTORIES, filename=".git",)

    # Cleanup
    foss.delete_upload(vcs_upload)


def test_upload_ignore_scm(foss: Fossology):
    vcs = {
        "vcsType": "git",
        "vcsUrl": "https://github.com/fossology/fossology-python",
        "vcsName": "fossology-python-github-master",
        "vcsUsername": "",
        "vcsPassword": "",
    }
    vcs_upload = foss.upload_file(
        foss.rootFolder,
        vcs=vcs,
        description="Test upload with ignore_scm flag",
        ignore_scm=False,
        access_level=AccessLevel.PUBLIC,
    )
    assert vcs_upload.uploadname == vcs["vcsName"]
    # FIXME: shall be fixed in the next release
    # assert foss.search(
    #    searchType=SearchTypes.DIRECTORIES, filename=".git",
    # ) == $something

    # Cleanup
    foss.delete_upload(vcs_upload)


def test_upload_from_url(foss: Fossology):
    url = {
        "url": "https://github.com/fossology/fossology-python/archive/master.zip",
        "name": "fossology-python-master.zip",
        "accept": "zip",
        "reject": "",
        "maxRecursionDepth": "1",
    }
    url_upload = foss.upload_file(
        foss.rootFolder,
        url=url,
        description="Test upload from url via python lib",
        access_level=AccessLevel.PUBLIC,
    )
    assert url_upload.uploadname == url["name"]

    # Cleanup
    foss.delete_upload(url_upload)


def test_empty_upload(foss: Fossology):
    empty_upload = foss.upload_file(
        foss.rootFolder,
        description="Test empty upload",
        access_level=AccessLevel.PUBLIC,
    )
    assert not empty_upload


def test_move_upload_nogroup(foss: Fossology, upload: Upload, move_folder: Folder):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.move_upload(upload, move_folder, group="test")
    assert (
        f"Moving upload {upload.id} for group test in folder {move_folder.id} not authorized"
        in str(excinfo.value)
    )


@responses.activate
def test_move_copy_upload_error(
    foss_server: str, foss: Fossology, upload: Upload, move_folder: Folder
):
    responses.add(
        responses.PATCH, f"{foss_server}/api/v1/uploads/{upload.id}", status=404
    )
    responses.add(
        responses.PUT, f"{foss_server}/api/v1/uploads/{upload.id}", status=404
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.move_upload(upload, move_folder)
    assert f"Unable to move upload {upload.uploadname} to {move_folder.name}" in str(
        excinfo.value
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.copy_upload(upload, move_folder)
    assert f"Unable to copy upload {upload.uploadname} to {move_folder.name}" in str(
        excinfo.value
    )


def test_move_copy_upload(foss: Fossology, upload: Upload, move_folder: Folder):
    foss.move_upload(upload, move_folder)
    moved_upload = foss.detail_upload(upload.id)
    assert moved_upload.folderid == move_folder.id

    # FIXME: recursion due to https://github.com/fossology/fossology/pull/1748?
    foss.copy_upload(moved_upload, foss.rootFolder)
    list_uploads = foss.list_uploads()
    test_upload = None
    for upload in list_uploads:
        if upload.folderid == foss.rootFolder.id:
            test_upload = upload
    if not test_upload:
        print("Copying uploads didn't work")
    else:
        print("Copying uploads works again, replace log output with assert")
    # assert upload


def test_move_copy_arbitrary_folder(foss: Fossology, upload: Upload):
    non_folder = Folder(secrets.randbelow(1000), "Non folder", "", foss.rootFolder)
    with pytest.raises(AuthorizationError):
        foss.move_upload(upload, non_folder)
    with pytest.raises(AuthorizationError):
        foss.copy_upload(upload, non_folder)


@responses.activate
def test_upload_summary_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(
        responses.GET, f"{foss_server}/api/v1/uploads/{upload.id}/summary", status=404
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_summary(upload)
    assert f"No summary for upload {upload.uploadname} (id={upload.id})" in str(
        excinfo.value
    )


def test_upload_summary(foss: Fossology, scanned_upload: Upload):
    summary = foss.upload_summary(scanned_upload)
    assert summary.clearingStatus == "Open"
    assert (
        f"Clearing status for '{summary.uploadName}' is '{summary.clearingStatus}', "
        f"main license = {summary.mainLicense}"
    ) in str(summary)
    assert not summary.mainLicense


def test_upload_summary_nogroup(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_summary(upload, group="test")
    assert (
        f"Getting summary of upload {upload.id} for group test not authorized"
        in str(excinfo.value)
    )


@responses.activate
def test_upload_licenses_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(
        responses.GET, f"{foss_server}/api/v1/uploads/{upload.id}/licenses", status=404
    )
    responses.add(
        responses.GET, f"{foss_server}/api/v1/uploads/{upload.id}/licenses", status=412
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_licenses(upload)
    assert f"No licenses for upload {upload.uploadname} (id={upload.id})" in str(
        excinfo.value
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_licenses(upload)
    assert (
        f"Unable to get licenses from nomos for {upload.uploadname} (id={upload.id})"
        in str(excinfo.value)
    )


def test_upload_licenses(foss: Fossology, scanned_upload: Upload):
    licenses = foss.upload_licenses(scanned_upload)
    assert len(licenses) == 56


def test_upload_licenses_containers(foss: Fossology, scanned_upload: Upload):
    licenses = foss.upload_licenses(scanned_upload, containers=True)
    assert len(licenses) == 56


def test_upload_licenses_unscheduled(foss: Fossology, scanned_upload: Upload):
    licenses = foss.upload_licenses(scanned_upload, agent="ojo")
    assert not licenses[0].get("agentFindings")


def test_upload_licenses_from_agent(foss: Fossology, scanned_upload: Upload):
    licenses = foss.upload_licenses(scanned_upload, agent="monk")
    assert len(licenses) == 23


def test_upload_licenses_nogroup(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_licenses(upload, group="test")
    assert (
        f"Getting license for upload {upload.id} for group test not authorized"
        in str(excinfo.value)
    )


def test_delete_unknown_upload(foss: Fossology):
    upload = Upload(
        foss.rootFolder,
        "Root Folder",
        secrets.randbelow(1000),
        "",
        "Non Upload",
        "2020-05-05",
        "0",
        "sha",
    )
    with pytest.raises(FossologyApiError):
        foss.delete_upload(upload)


def test_delete_upload_nogroup(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.delete_upload(upload, group="test")
    assert f"Deleting upload {upload.id} for group test not authorized" in str(
        excinfo.value
    )
