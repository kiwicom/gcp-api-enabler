import json
import pytest
import os
import base64
import main
from mock import Mock

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def datafile(filename):
    return os.path.join(DATA_DIR, filename)


def test_api_enabler_http_default_settings():
    main.get_credentials = Mock(return_value='')
    main.get_enabled_services = Mock(return_value=[])
    main.enable_service = Mock(return_value=True)

    with open(datafile('projects_list.json')) as f:
        projects_data = json.load(f)
        main.get_projects = Mock(return_value=projects_data)

    response = json.loads(main.api_enabler_http({}))

    assert 'enabledServices' in response
    assert '123456789010' in response['enabledServices']
    assert '123456789011' in response['enabledServices']
    assert '123456789012' in response['enabledServices']
    assert 'projects/123456789010/services/compute.googleapis.com' in response['enabledServices']['123456789010']
    assert 'projects/123456789010/services/cloudresourcemanager.googleapis.com' in response['enabledServices'][
        '123456789010']
    assert 'projects/123456789010/services/container.googleapis.com' in response['enabledServices']['123456789010']
    assert 'projects/123456789010/services/storage-api.googleapis.com' in response['enabledServices']['123456789010']
    assert 'projects/123456789011/services/compute.googleapis.com' in response['enabledServices']['123456789011']
    assert 'projects/123456789011/services/cloudresourcemanager.googleapis.com' in response['enabledServices'][
        '123456789011']
    assert 'projects/123456789011/services/container.googleapis.com' in response['enabledServices']['123456789011']
    assert 'projects/123456789011/services/storage-api.googleapis.com' in response['enabledServices']['123456789011']
    assert 'projects/123456789012/services/compute.googleapis.com' in response['enabledServices']['123456789012']
    assert 'projects/123456789012/services/cloudresourcemanager.googleapis.com' in response['enabledServices'][
        '123456789012']
    assert 'projects/123456789012/services/container.googleapis.com' in response['enabledServices']['123456789012']
    assert 'projects/123456789012/services/storage-api.googleapis.com' in response['enabledServices']['123456789012']


def test_api_enabler_http_changed_init_services():
    main.get_credentials = Mock(return_value='')
    main.get_enabled_services = Mock(return_value=[])
    main.enable_service = Mock(return_value=True)
    main.init_services = Mock(return_value={
        'container.googleapis.com': False,
        'compute.googleapis.com': True,
        'storage-api.googleapis.com': False,
        'cloudresourcemanager.googleapis.com': False
    })

    with open(datafile('projects_list.json')) as f:
        projects_data = json.load(f)
        main.get_projects = Mock(return_value=projects_data)

    response = json.loads(main.api_enabler_http({}))

    assert 'enabledServices' in response
    assert '123456789010' in response['enabledServices']
    assert '123456789011' in response['enabledServices']
    assert '123456789012' in response['enabledServices']
    assert 'projects/123456789010/services/compute.googleapis.com' in response['enabledServices']['123456789010']
    assert 'projects/123456789011/services/compute.googleapis.com' in response['enabledServices']['123456789011']
    assert 'projects/123456789012/services/compute.googleapis.com' in response['enabledServices']['123456789012']


def test_api_enabler_listener_without_data():
    with pytest.raises(ValueError, message="Received data is empty."):
        data = {}
        main.api_enabler_listener(data)


def test_api_enabler_listener_with_wrong_data():
    with pytest.raises(ValueError, message="Received data is not related to CreateObject event"):
        data = {"data": base64.b64encode("{\"protoPayload\": {\"methodName\": \"Wrooong\"}}")}
        main.api_enabler_listener(data)


def test_api_enabler_listener_default_settings():
    main.get_credentials = Mock(return_value='')
    main.get_enabled_services = Mock(return_value=[])
    main.enable_service = Mock(return_value=True)
    main.init_services = Mock(return_value={
        'container.googleapis.com': True,
        'compute.googleapis.com': True,
        'storage-api.googleapis.com': True,
        'cloudresourcemanager.googleapis.com': True
    })

    with open(datafile('create_project_logs.json')) as f:
        raw_data = f.read()
        data = {"data": base64.b64encode(raw_data)}

    response = json.loads(main.api_enabler_listener(data))

    assert 'enabledServices' in response
    assert '37559420870' in response['enabledServices']
    assert 'projects/37559420870/services/compute.googleapis.com' in response['enabledServices']['37559420870']
    assert 'projects/37559420870/services/cloudresourcemanager.googleapis.com' in response['enabledServices'][
        '37559420870']
    assert 'projects/37559420870/services/container.googleapis.com' in response['enabledServices']['37559420870']
    assert 'projects/37559420870/services/storage-api.googleapis.com' in response['enabledServices']['37559420870']


def test_api_enabler_listener_changed_enabled_services():
    main.get_credentials = Mock(return_value='')
    main.get_enabled_services = Mock(
        return_value=[{
            'name': 'projects/37559420870/services/storage-api.googleapis.com',
            'config': {'name': 'storage-api.googleapis.com'},
            'parent': 'nevermind',
            'state': 'ENABLED'}
        ]
    )
    main.enable_service = Mock(return_value=True)

    with open(datafile('create_project_logs.json')) as f:
        raw_data = f.read()
        data = {"data": base64.b64encode(raw_data)}

    response = json.loads(main.api_enabler_listener(data))

    assert 'enabledServices' in response
    assert '37559420870' in response['enabledServices']
    assert 'projects/37559420870/services/compute.googleapis.com' in response['enabledServices']['37559420870']
    assert 'projects/37559420870/services/cloudresourcemanager.googleapis.com' in response['enabledServices'][
        '37559420870']
    assert 'projects/37559420870/services/container.googleapis.com' in response['enabledServices']['37559420870']


def test_api_enabler_listener_changed_init_services():
    main.get_credentials = Mock(return_value='')
    main.get_enabled_services = Mock(return_value=[])
    main.enable_service = Mock(return_value=True)
    main.init_services = Mock(return_value={
        'container.googleapis.com': True,
        'compute.googleapis.com': False,
        'storage-api.googleapis.com': True,
        'cloudresourcemanager.googleapis.com': True
    })

    with open(datafile('create_project_logs.json')) as f:
        raw_data = f.read()
        data = {"data": base64.b64encode(raw_data)}

    response = json.loads(main.api_enabler_listener(data))

    assert 'enabledServices' in response
    assert '37559420870' in response['enabledServices']
    assert 'projects/37559420870/services/cloudresourcemanager.googleapis.com' in response['enabledServices'][
        '37559420870']
    assert 'projects/37559420870/services/container.googleapis.com' in response['enabledServices']['37559420870']
    assert 'projects/37559420870/services/storage-api.googleapis.com' in response['enabledServices']['37559420870']
