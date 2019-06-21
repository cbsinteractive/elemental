from client import ElementalLive
from client import InvalidRequest
from client import InvalidResponse
import mock
import requests
import os
import pytest

USER = "FAKE"
API_KEY = "FAKE"
ELEMENTAL_ADDRESS = "FAKE_ADDRESS.com"
HEADERS = {'Accept': 'application/xml', 'Content-Type': 'application/xml'}
REQUEST_BODY = "<live_event>FAKE</live_event>"


def mock_response(status=200, content=None, text=None,
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
    e = ElementalLive(ELEMENTAL_ADDRESS)
    assert e.server_ip == ELEMENTAL_ADDRESS


def test_generate_header_with_authentication_should_contain_user():
    """"test generate function"""
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    headers = client.generate_headers(f'{ELEMENTAL_ADDRESS}/live_events')
    assert headers['X-Auth-User'] == USER
    assert headers['Accept'] == 'application/xml'
    assert headers['Content-Type'] == 'application/xml'


def test_genterate_header_without_authentication_should_not_contain_user():
    """"test generate function"""
    client = ElementalLive(ELEMENTAL_ADDRESS)
    headers = client.generate_headers()
    assert 'X-Auth-User' not in headers
    assert headers['Accept'] == 'application/xml'
    assert headers['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_send_request_should_call_request_as_expected(mock_request):
    """test send request method
    to call request method"""
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    mock_request.return_value = mock_response(status=200)
    client.send_request(
        'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)

    request_to_elemental = mock_request.call_args_list[0][1]
    assert request_to_elemental['url'] == f'{ELEMENTAL_ADDRESS}/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'


@mock.patch('requests.request')
def test_send_request_should_return_response_on_correct_status_code(
        mock_request):
    """test send request method on 201 or 200"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    mock_request.return_value = mock_response(
        status=201, text=response_from_elemental_api)

    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    response = client.send_request(
        'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)

    assert response.text == response_from_elemental_api
    assert response.status_code == 201


@mock.patch('requests.request')
def test_send_request_should_raise_InvalidRequest_on_RequestException(
        mock_request):
    """test create_event method on invalid request"""
    mock_request.side_effect = requests.exceptions.RequestException()

    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    with pytest.raises(InvalidRequest):
        client.send_request(
            'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)


@mock.patch('requests.request')
def test_send_request_should_raise_InvalidResponse_on_invalid_status_code(
        mock_request):
    """test create_event method on invalid response"""
    response_from_elemental_api = open(
        'live/templates/fail_to_create_response.xml').read()
    mock_request.return_value = mock_response(
        status=404, text=response_from_elemental_api)

    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    with pytest.raises(InvalidResponse) as exc_info:
        client.send_request(
            'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)

    assert str(exc_info.value).endswith(
        f"Response: 404\n{response_from_elemental_api}")


def test_create_event_should_call_send_request_as_expect_and_return_event_id():
    """test create method"""
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    client.send_request.return_value = mock_response(
        status=201, content=response_from_elemental_api)

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

    response_from_elemental_api = client.send_request.call_args_list[0][1]
    assert response_from_elemental_api['http_method'] == 'POST'
    assert response_from_elemental_api['url'] == \
        f'{ELEMENTAL_ADDRESS}/live_events'
    assert response_from_elemental_api['headers'] == HEADERS
    assert event_id == '80'


def test_delete_event_should_call_send_request_as_expect():
    """test delete method"""
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(status=200)

    event_id = 999
    client.delete_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='DELETE',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}', headers=HEADERS)


def test_start_event_should_call_send_request_as_expect():
    """test start method"""
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()

    client.send_request.return_value = mock_response(status=200)

    event_id = 999
    client.start_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='POST',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}/start',
        headers=HEADERS, body="<start></start>")


def test_stop_event_should_call_send_request_as_expect():
    """test stop method"""
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(status=200)

    event_id = 999
    client.stop_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='POST',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}/stop',
        headers=HEADERS, body="<stop></stop>")
