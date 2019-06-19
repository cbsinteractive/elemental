from client import ElementalLive
from client import InvalidRequestOrResponse
import mock
import os
import re
import pytest

USER = "FAKE"
API_KEY = "FAKE"


def mock_response(status=200, content=None, text = None,
                  json_data=None, raise_for_status=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()

    # mock raise_for_status call w/optional error
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status

    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.text = text

    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp


def test_ElementalLive_should_receive_server_ip():
    e = ElementalLive('http://elemental.dev.cbsivideo.com/')
    assert e.server_ip == 'http://elemental.dev.cbsivideo.com/'


@mock.patch('requests.request')
def test_create_event_with_authentication_successfully(mock_request):
    """test create_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    mock_request.return_value = mock_response(
        status=201, content=response_from_elemental_api)

    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)
    event_id = client.create_event("live/templates/qvbr_mediastore.xml",
                                   {'username': os.getenv('ACCESS_KEY'),
                                    'password': os.getenv('SECRET_KEY'),
                                    'mediastore_container_master':
                                        'https://hu5n3jjiyi2jev.data.media'
                                        'store.us-east-1.amazonaws.com/master',
                                    'mediastore_container_backup':
                                        'https://hu5n3jjiyi2jev.data.medias'
                                        'tore.us-east-1.amazonaws.com/backup',
                                    'channel': "1", 'device_name': "0"})

    request_to_elemental = mock_request.call_args_list[0][1]
    assert request_to_elemental['url'] == 'http://elemental' \
                                          '.dev.cbsivideo.com/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
    assert event_id == "80"


@mock.patch('requests.request')
def test_create_event_with_authentication_raise_Error_on_other_status_codes(mock_request):
    """test create_event method"""
    response_from_elemental_api = open(
        'live/templates/fail_to_create_response.xml').read()

    mock_request.return_value = mock_response(
        status=422, text=response_from_elemental_api)

    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)
    with pytest.raises(InvalidRequestOrResponse) as exc_info:
        client.create_event("live/templates/qvbr_mediastore.xml",
                                       {'username': os.getenv('ACCESS_KEY'),
                                        'password': os.getenv('SECRET_KEY'),
                                        'mediastore_container_master':
                                        'https://hu5n3jjiyi2jev.data.media'
                                        'store.us-east-1.amazonaws.com/master',
                                        'mediastore_container_backup':
                                        'https://hu5n3jjiyi2jev.data.medias'
                                        'tore.us-east-1.amazonaws.com/backup',
                                        'channel': "1", 'device_name': "0"})

    request_to_elemental = mock_request.call_args_list[0][1]
    assert str(exc_info.value) == (f"Fail to create event\n"
                                   f"Response: " + "422\n" + response_from_elemental_api)

    assert request_to_elemental['url'] == 'http://elemental' \
                                          '.dev.cbsivideo.com/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_create_event_without_authentication_successfully(mock_request):
    """test create_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    mock_request.return_value = mock_response(
        status=201, content=response_from_elemental_api)

    client = ElementalLive("http://elemental.dev.cbsivideo.com")
    event_id = client.create_event("live/templates/qvbr_mediastore.xml",
                                   {'username': os.getenv('ACCESS_KEY'),
                                    'password': os.getenv('SECRET_KEY'),
                                    'mediastore_container_master':
                                        'https://hu5n3jjiyi2jev.data.media'
                                        'store.us-east-1.amazonaws.com/master',
                                    'mediastore_container_backup':
                                        'https://hu5n3jjiyi2jev.data.medias'
                                        'tore.us-east-1.amazonaws.com/backup',
                                    'channel': "1", 'device_name': "0"})

    request_to_elemental = mock_request.call_args_list[0][1]
    assert request_to_elemental['url'] == 'http://elemental' \
                                          '.dev.cbsivideo.com/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
    assert event_id == "80"


@mock.patch('requests.request')
def test_delete_event_with_authentication_successfully(mock_request):
    """test delete_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_delete.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    # Mock delete function
    client.delete_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'DELETE'


@mock.patch('requests.request')
def test_delete_event_with_authentication_raise_Error_on_other_status_codes(mock_request):
    """test delete_event method"""
    response_from_elemental_api = open(
        'live/templates/fail_to_delete_response.xml').read()
    mock_request.return_value = mock_response(
        status=404, text=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    with pytest.raises(InvalidRequestOrResponse) as exc_info:
        # Mock delete function
        event_id = 42
        client.delete_event(event_id)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert str(exc_info.value) == (f"Fail to delete event with id: {event_id}\n"
                                   f"Response: " + "404\n" + response_from_elemental_api)
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'DELETE'


@mock.patch('requests.request')
def test_delete_event_without_authentication_successfully(mock_request):
    """test delete_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_delete.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)')
    client = ElementalLive("http://elemental.dev.cbsivideo.com")

    # Mock delete function
    client.delete_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'DELETE'


@mock.patch('requests.request')
def test_start_event_with_authentication_successfully(mock_request):
    """test start_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/start')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    # Mock start function
    client.start_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'

@mock.patch('requests.request')
def test_start_event_with_authentication_raise_Error_on_other_status_codes(mock_request):
    """test start_event method"""
    response_from_elemental_api = open(
        'live/templates/fail_to_start_response.xml').read()
    mock_request.return_value = mock_response(
        status=404, text=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/start')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    with pytest.raises(InvalidRequestOrResponse) as exc_info:
        # Mock start function
        event_id = 42
        client.start_event(event_id)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert str(exc_info.value) == (f"Fail to start event with id: {event_id}\n"
                                   f"Response: " + "404\n" + response_from_elemental_api)
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_start_event_without_authentication_successfully(mock_request):
    """test start_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/start')
    client = ElementalLive("http://elemental.dev.cbsivideo.com")

    # Mock start function
    client.start_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_stop_event_with_authentication_successfully(mock_request):
    """test stop_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/stop')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    # Mock stop function
    client.stop_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_stop_event_with_authentication_raise_Error_on_other_status_codes(mock_request):
    """test start_event method"""
    response_from_elemental_api = open(
        'live/templates/fail_to_stop_response.xml').read()
    mock_request.return_value = mock_response(
        status=404, text=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/stop')
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)

    with pytest.raises(InvalidRequestOrResponse) as exc_info:
        # Mock stop function
        event_id = 42
        client.stop_event(event_id)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert str(exc_info.value) == (f"Fail to stop event with id: {event_id}\n"
                                   f"Response: " + "404\n" + response_from_elemental_api)
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_stop_event_without_authentication_successfully(mock_request):
    """test stop_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_start.xml').read()
    mock_request.return_value = mock_response(
        status=200, content=response_from_elemental_api)

    # Set match pattern
    delete_pattern = re.compile(
        r'http://elemental.dev.cbsivideo.com/live_events/(\d+)/stop')
    client = ElementalLive("http://elemental.dev.cbsivideo.com")

    # Mock delete function
    client.stop_event(event_id=42)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert delete_pattern.match(request_to_elemental['url'])
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
