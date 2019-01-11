import json
import base64

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

PROJECT_ACTIVE = 'ACTIVE'
STATE_DISABLED = 'DISABLED'
STATE_ENABLED = 'ENABLED'


def initial_services():
    """Preferred services should be stated here.
    :return: dict
    """
    return {
        'container.googleapis.com': True,
        'compute.googleapis.com': True,
        'storage-api.googleapis.com': True,
        'cloudresourcemanager.googleapis.com': True,
        'sqladmin.googleapis.com': True,
    }


def init_response_data():
    """Inits response data
    :return: dict
    """
    return {
        'enabledServices': {}
    }


def api_enabler_http(request):
    """Gets triggered by simple HTTP GET request.
    :param request: flask.Request
    :return: Response
    """
    response_data = init_response_data()

    credentials = get_credentials()

    projects = get_projects(credentials)

    for project in projects:
        if project['lifecycleState'] != PROJECT_ACTIVE:
            continue
        project_number = project['projectNumber']
        response_data['enabledServices'][project_number] = enable_services(
            credentials=credentials,
            project_number=project_number
        )

    return json.dumps(response_data, indent=4)


def api_enabler_listener(data, context):
    """Gets triggered by Pub/Sub topic.
    :param data: dict: The dictionary with data specific to this type of event.
    :param context: (google.cloud.functions.Context): The Cloud Functions event metadata.
    :return: Response
    """
    response_data = init_response_data()

    credentials = get_credentials()

    if 'data' not in data:
        raise ValueError("Received data is empty.")

    json_data = json.loads('{}'.format(base64.b64decode(data['data']).decode('utf-8')))
    method_name = json_data['protoPayload']['methodName']

    if method_name != 'CreateProject':
        raise ValueError("Received data is not related to CreateObject event.")

    project_number = json_data['protoPayload']['request']['project']['projectNumber']

    response_data['enabledServices'][project_number] = enable_services(
        credentials=credentials,
        project_number=project_number
    )

    return json.dumps(response_data, indent=4)


def enable_services(credentials, project_number):
    """Will enable services for given project number.
    :param project_number: string
    :param credentials: Any
    :return: services: dict
    """
    enabled_services = []

    services_to_enable = initial_services()

    project_name = 'projects/' + project_number

    services = get_enabled_services(credentials=credentials, project_name=project_name)

    for service in services:
        service_name = service['config']['name']

        if service_name in services_to_enable:
            services_to_enable[service_name] = False

    for service_name, should_enable in services_to_enable.items():
        if should_enable:
            service_long_name = project_name + '/services/' + service_name
            enable_service(credentials=credentials, service_name=service_long_name)
            enabled_services.append(service_long_name)

    return enabled_services


def get_projects(credentials):
    """Returns all organization projects.
    :param credentials: Any
    :return: projects: dict
    """
    organization_projects = []

    cloud_resource_manager = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    projects_request = cloud_resource_manager.projects().list()

    while projects_request is not None:
        projects = projects_request.execute()

        if 'projects' not in projects:
            break

        organization_projects = organization_projects + projects['projects']

        projects_request = cloud_resource_manager.projects().list_next(
            previous_request=projects_request,
            previous_response=projects
        )

    return organization_projects


def get_enabled_services(credentials, project_name):
    """Returns already enabled services for given project.
    :param credentials: Any
    :param project_name: string
    :return: services: dict
    """
    enabled_services = []

    service_usage = discovery.build('serviceusage', 'v1', credentials=credentials)

    services_filter = 'state:' + STATE_ENABLED
    services_request = service_usage.services().list(
        parent=project_name,
        pageSize=200,
        filter=services_filter
    )

    while services_request is not None:
        services = services_request.execute()

        if 'services' not in services:
            break

        enabled_services = enabled_services + services['services']

        services_request = service_usage.services().list_next(
            previous_request=services_request,
            previous_response=services
        )

    return enabled_services


def enable_service(credentials, service_name):
    """Will enable given service.
    :param credentials: Any
    :param service_name: string
    :return: bool
    """
    service_usage = discovery.build('serviceusage', 'v1', credentials=credentials)

    service_usage.services().enable(name=service_name).execute()


def get_credentials():
    """Returns Google Credentials.
    :return: GoogleCredentials
    """
    return GoogleCredentials.get_application_default()
