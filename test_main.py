import json
import pytest
import base64
import os

from unittest.mock import Mock
from pathlib import Path
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

import main as uut

DATA_DIR = Path.cwd().joinpath("test_data")


def datafile(filename):
    return DATA_DIR.joinpath(filename)


def test_api_enabler_http_default_settings(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    mocker.patch.object(discovery, "build")
    mocker.patch.dict(
        os.environ,
        {
            "SERVICES_TO_ENABLE": "compute.googleapis.com,cloudresourcemanager.googleapis.com,container.googleapis.com,"
            "storage-api.googleapis.com"
        },
    )

    with Path.open(datafile("projects_list.json")) as f:
        projects_data = json.load(f)
        mocker.patch.object(uut, "get_projects", return_value=projects_data)

    request = Mock(get_json=Mock(return_value={}), args={})
    response = json.loads(uut.api_enabler_http(request))

    assert "enabledServices" in response
    assert "123456789010" in response["enabledServices"]
    assert "123456789011" in response["enabledServices"]
    assert "123456789012" in response["enabledServices"]
    assert (
        "projects/123456789010/services/compute.googleapis.com"
        in response["enabledServices"]["123456789010"]
    )
    assert (
        "projects/123456789010/services/cloudresourcemanager.googleapis.com"
        in response["enabledServices"]["123456789010"]
    )
    assert (
        "projects/123456789010/services/container.googleapis.com"
        in response["enabledServices"]["123456789010"]
    )
    assert (
        "projects/123456789010/services/storage-api.googleapis.com"
        in response["enabledServices"]["123456789010"]
    )
    assert (
        "projects/123456789011/services/compute.googleapis.com"
        in response["enabledServices"]["123456789011"]
    )
    assert (
        "projects/123456789011/services/cloudresourcemanager.googleapis.com"
        in response["enabledServices"]["123456789011"]
    )
    assert (
        "projects/123456789011/services/container.googleapis.com"
        in response["enabledServices"]["123456789011"]
    )
    assert (
        "projects/123456789011/services/storage-api.googleapis.com"
        in response["enabledServices"]["123456789011"]
    )
    assert (
        "projects/123456789012/services/compute.googleapis.com"
        in response["enabledServices"]["123456789012"]
    )
    assert (
        "projects/123456789012/services/cloudresourcemanager.googleapis.com"
        in response["enabledServices"]["123456789012"]
    )
    assert (
        "projects/123456789012/services/container.googleapis.com"
        in response["enabledServices"]["123456789012"]
    )
    assert (
        "projects/123456789012/services/storage-api.googleapis.com"
        in response["enabledServices"]["123456789012"]
    )


def test_api_enabler_http_changed_init_services(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    mocker.patch.object(discovery, "build")
    mocker.patch.dict(os.environ, {"SERVICES_TO_ENABLE": "compute.googleapis.com"})

    with Path.open(datafile("projects_list.json")) as f:
        projects_data = json.load(f)
        mocker.patch.object(uut, "get_projects", return_value=projects_data)

    request = Mock(get_json=Mock(return_value={}), args={})
    response = json.loads(uut.api_enabler_http(request))

    assert "enabledServices" in response
    assert "123456789010" in response["enabledServices"]
    assert "123456789011" in response["enabledServices"]
    assert "123456789012" in response["enabledServices"]
    assert (
        "projects/123456789010/services/compute.googleapis.com"
        in response["enabledServices"]["123456789010"]
    )
    assert (
        "projects/123456789011/services/compute.googleapis.com"
        in response["enabledServices"]["123456789011"]
    )
    assert (
        "projects/123456789012/services/compute.googleapis.com"
        in response["enabledServices"]["123456789012"]
    )


def test_api_enabler_listener_without_data(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    with pytest.raises(ValueError, message="Received data is empty."):
        data = {}
        uut.api_enabler_listener(data, None)


def test_api_enabler_listener_with_wrong_data(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    with pytest.raises(
        ValueError, message="Received data is not related to CreateObject event"
    ):
        data = {
            "data": base64.b64encode(
                '{"protoPayload": {"methodName": "Wrooong"}}'.encode()
            )
        }
        uut.api_enabler_listener(data, None)


def test_api_enabler_listener_default_settings(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    mocker.patch.object(discovery, "build")
    mocker.patch.dict(
        os.environ,
        {
            "SERVICES_TO_ENABLE": "compute.googleapis.com,cloudresourcemanager.googleapis.com,container.googleapis.com,"
            "storage-api.googleapis.com"
        },
    )

    with Path.open(datafile("create_project_logs.json")) as f:
        raw_data = f.read()
        data = {"data": base64.b64encode(raw_data.encode())}

    response = json.loads(uut.api_enabler_listener(data, None))

    assert "enabledServices" in response
    assert "37559420870" in response["enabledServices"]
    assert (
        "projects/37559420870/services/compute.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/cloudresourcemanager.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/container.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/storage-api.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )


def test_api_enabler_listener_changed_enabled_services(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    mocker.patch.object(discovery, "build")
    mocker.patch.dict(
        os.environ,
        {
            "SERVICES_TO_ENABLE": "compute.googleapis.com,cloudresourcemanager.googleapis.com,container.googleapis.com"
        },
    )
    mocker.patch.object(
        uut,
        "get_enabled_services",
        return_value=[
            {
                "name": "projects/37559420870/services/storage-api.googleapis.com",
                "config": {"name": "storage-api.googleapis.com"},
                "parent": "nevermind",
                "state": "ENABLED",
            }
        ],
    )

    with Path.open(datafile("create_project_logs.json")) as f:
        raw_data = f.read()
        data = {"data": base64.b64encode(raw_data.encode())}

    response = json.loads(uut.api_enabler_listener(data, None))

    assert "enabledServices" in response
    assert "37559420870" in response["enabledServices"]
    assert (
        "projects/37559420870/services/compute.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/cloudresourcemanager.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/container.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )


def test_api_enabler_listener_changed_init_services(mocker):
    mocker.patch.object(GoogleCredentials, "get_application_default", return_value="")
    mocker.patch.object(discovery, "build")
    mocker.patch.dict(
        os.environ,
        {
            "SERVICES_TO_ENABLE": "cloudresourcemanager.googleapis.com,container.googleapis.com,storage-api.googleapis.com"
        },
    )

    with Path.open(datafile("create_project_logs.json")) as f:
        raw_data = f.read()
        data = {"data": base64.b64encode(raw_data.encode())}

    response = json.loads(uut.api_enabler_listener(data, None))

    assert "enabledServices" in response
    assert "37559420870" in response["enabledServices"]
    assert (
        "projects/37559420870/services/cloudresourcemanager.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/container.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
    assert (
        "projects/37559420870/services/storage-api.googleapis.com"
        in response["enabledServices"]["37559420870"]
    )
