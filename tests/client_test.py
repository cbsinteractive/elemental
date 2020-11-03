import json
import os

from unittest import mock
import pytest
import requests

from elemental.client import (ElementalException, ElementalLive, InvalidRequest,
                              InvalidResponse)

USER = "FAKE"
API_KEY = "FAKE"
ELEMENTAL_ADDRESS = "FAKE_ADDRESS.com"
HEADERS = {'Accept': 'application/xml', 'Content-Type': 'application/xml'}
REQUEST_BODY = "<live_event>FAKE</live_event>"
TIMEOUT = 10


def file_fixture(file_name):
    with open(os.path.join("tests/fixtures", file_name)) as f:
        return f.read()


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
    assert e.server_url == ELEMENTAL_ADDRESS


def test_generate_header_with_authentication_should_contain_user():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    headers = client.generate_headers(f'{ELEMENTAL_ADDRESS}/live_events')
    assert headers['X-Auth-User'] == USER
    assert headers['Accept'] == 'application/xml'
    assert headers['Content-Type'] == 'application/xml'


def test_generate_header_without_authentication_should_not_contain_user():
    client = ElementalLive(ELEMENTAL_ADDRESS)
    headers = client.generate_headers()
    assert 'X-Auth-User' not in headers
    assert headers['Accept'] == 'application/xml'
    assert headers['Content-Type'] == 'application/xml'


def test_send_request_should_call_request_as_expected():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.session.request = mock.MagicMock(
        return_value=mock_response(status=200))
    client.send_request(
        'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY, timeout=TIMEOUT)

    request_to_elemental = client.session.request.call_args_list[0][1]
    assert request_to_elemental['url'] == f'{ELEMENTAL_ADDRESS}/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
    assert request_to_elemental['timeout'] == TIMEOUT


def test_send_request_should_return_response_on_correct_status_code():
    response_from_elemental_api = file_fixture('success_response_for_create.xml')
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.session.request = mock.MagicMock(return_value=mock_response(
        status=201, text=response_from_elemental_api))
    response = client.send_request(
        'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)

    assert response.text == response_from_elemental_api
    assert response.status_code == 201


def test_send_request_should_raise_InvalidRequest_on_RequestException():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.session.request = mock.MagicMock(
        side_effect=requests.exceptions.RequestException())

    with pytest.raises(InvalidRequest):
        client.send_request(
            'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)


def test_send_request_should_raise_InvalidResponse_on_invalid_status_code():
    response_from_elemental_api = file_fixture('fail_to_create_response.xml')

    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.session.request = mock.MagicMock(return_value=mock_response(
        status=404, text=response_from_elemental_api))

    with pytest.raises(InvalidResponse) as exc_info:
        client.send_request(
            'POST', f'{ELEMENTAL_ADDRESS}/live_events', HEADERS, REQUEST_BODY)

    assert str(exc_info.value).endswith(
        f"Response: 404\n{response_from_elemental_api}")


def test_create_event():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    elemental_response = file_fixture('success_response_for_create.xml')

    client.send_request.return_value = mock_response(
        status=201, content=elemental_response)

    event_id = client.create_event('<new-event />')

    client.send_request.assert_called_once_with(
        http_method='POST', url='FAKE_ADDRESS.com/live_events',
        headers={'Accept': 'application/xml',
                 'Content-Type': 'application/xml'},
        body='<new-event />', timeout=None)

    send_mock_call = client.send_request.call_args_list[0][1]
    assert send_mock_call['http_method'] == 'POST'
    assert send_mock_call['url'] == f'{ELEMENTAL_ADDRESS}/live_events'
    assert send_mock_call['headers'] == HEADERS
    assert event_id == {'id': '53'}


def test_update_event():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS
    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(
        status=200)

    client.update_event('53', '<updated-event />')

    client.send_request.assert_called_once_with(
        http_method='PUT', url='FAKE_ADDRESS.com/live_events/53',
        headers={'Accept': 'application/xml',
                 'Content-Type': 'application/xml'},
        body='<updated-event />', timeout=None)
    send_mock_call = client.send_request.call_args_list[0][1]
    assert send_mock_call['http_method'] == 'PUT'
    assert send_mock_call['url'] == f'{ELEMENTAL_ADDRESS}/live_events/53'
    assert send_mock_call['headers'] == HEADERS


def test_update_event_with_restart():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS
    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(
        status=200)

    client.update_event('53', '<updated-event />', restart=True)

    client.send_request.assert_called_once_with(
        http_method='PUT', url='FAKE_ADDRESS.com/live_events/53?unlocked=1',
        headers={'Accept': 'application/xml',
                 'Content-Type': 'application/xml'},
        body='<updated-event />', timeout=None)
    send_mock_call = client.send_request.call_args_list[0][1]
    assert send_mock_call['http_method'] == 'PUT'
    assert send_mock_call['url'] == f'{ELEMENTAL_ADDRESS}/live_events/53?unlocked=1'
    assert send_mock_call['headers'] == HEADERS


def test_delete_event_should_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(status=200)

    event_id = '999'
    client.delete_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='DELETE',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}', headers=HEADERS, timeout=None)


def test_cancel_event_should_call_send_request_as_expected():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(status=200)

    event_id = '999'
    client.cancel_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='POST',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}/cancel', headers=HEADERS, timeout=None)


def test_start_event_should_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()

    client.send_request.return_value = mock_response(status=200)

    event_id = '999'
    client.start_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='POST',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}/start',
        headers=HEADERS, body="<start></start>", timeout=None)


def test_reset_event_should_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()

    client.send_request.return_value = mock_response(status=200)

    event_id = '999'
    client.reset_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='POST',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}/reset',
        headers=HEADERS, body='', timeout=None)


def test_stop_event_should_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(status=200)

    event_id = '999'
    client.stop_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='POST',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}/stop',
        headers=HEADERS, body="<stop></stop>", timeout=None)


def send_request_side_effect(**kwargs):
    if kwargs['url'] == f'{ELEMENTAL_ADDRESS}/live_events':
        return mock_response(status=200,
                             text=file_fixture('sample_event_list.xml'))
    else:
        return mock_response(status=200,
                             text=file_fixture('sample_device_list.xml'))


def test_find_devices_in_use_will_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = \
        mock_response(status=200,
                      text=file_fixture('sample_event_list.xml'))

    client.find_devices_in_use()

    client.send_request.assert_called_with(http_method="GET",
                                           url=f'{ELEMENTAL_ADDRESS}'
                                           f'/live_events?'
                                           f'filter=active', headers=HEADERS, timeout=None)


def test_find_devices_in_use_will_return_in_used_devices():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = \
        mock_response(status=200,
                      text=file_fixture('sample_event_list.xml'))

    devices = client.find_devices_in_use()
    assert devices == {'HD-SDI 1'}


def test_get_input_devices_will_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.find_devices_in_use = mock.Mock()
    client.find_devices_in_use.return_value = ("HD-SDI 1",)
    client.send_request.return_value = \
        mock_response(status=200,
                      text=file_fixture('sample_device_list.xml'))

    client.get_input_devices()

    client.send_request.\
        assert_called_with(http_method="GET",
                           url=f'{ELEMENTAL_ADDRESS}/devices', headers=HEADERS, timeout=None)


def test_get_input_devices_will_get_right_devices_info():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.find_devices_in_use = mock.Mock()
    client.find_devices_in_use.return_value = ("HD-SDI 1",)
    client.send_request.return_value = \
        mock_response(status=200,
                      text=file_fixture('sample_device_list.xml'))

    res = client.get_input_devices()
    assert res == [{"id": "1",
                    "name": None, "device_name": "HD-SDI 1",
                    "device_number": "0", "device_type": "AJA",
                    "description": "AJA Capture Card",
                    "channel": "1", "channel_type": "HD-SDI",
                    "quad": "false", "availability": False},
                   {"id": "2",
                    "name": None, "device_name": "HD-SDI 2",
                    "device_number": "0", "device_type": "AJA",
                    "description": "AJA Capture Card",
                    "channel": "2", "channel_type": "HD-SDI",
                    "quad": "false", "availability": True}]


def test_get_input_device_by_id_will_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.find_devices_in_use = mock.Mock()
    client.find_devices_in_use.return_value = ("HD-SDI 1",)
    client.send_request.return_value = \
        mock_response(status=200,
                      text=file_fixture('sample_single_device.xml'))

    client.get_input_device_by_id('2')

    client.send_request.\
        assert_called_with(http_method="GET",
                           url=f'{ELEMENTAL_ADDRESS}/devices/2',
                           headers=HEADERS, timeout=None)


def test_get_input_device_by_id_will_get_right_devices_info():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.find_devices_in_use = mock.Mock()
    client.find_devices_in_use.return_value = ("HD-SDI 1",)
    client.send_request.return_value = \
        mock_response(status=200,
                      text=file_fixture('sample_single_device.xml'))

    res = client.get_input_device_by_id('2')
    assert res == {"id": "2",
                   "name": None, "device_name": "HD-SDI 2",
                   "device_number": "0", "device_type": "AJA",
                   "description": "AJA Capture Card",
                   "channel": "2", "channel_type": "HD-SDI",
                   "quad": "false", 'availability': True}


def test_get_preview_will_parse_response_json_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(
        status=200, text=file_fixture(
            'success_response_for_generate_preview.json'))

    response = client.generate_preview('2')

    assert response == {
        'preview_url': f'{ELEMENTAL_ADDRESS}/'
                       f'images/thumbs/p_1563568669_job_0.jpg'}


def test_get_preview_will_raise_ElementalException_if_preview_unavaliable():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    client.send_request.return_value = mock_response(
        status=200, text=json.dumps({"type": "error",
                                     "message": "Input is invalid. "
                                                "Device already in use."}))

    with pytest.raises(ElementalException) as exc_info:
        client.generate_preview('1')

    respond_text = json.dumps({'type': 'error',
                               'message': 'Input is invalid. '
                                          'Device already in use.'})
    assert str(exc_info.value).endswith(
        f"Response: 200\n"
        f"{respond_text}")


def test_describe_event_will_call_send_request_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS

    client.send_request = mock.Mock()
    response_from_elemental_api = file_fixture('sample_event.xml')
    client.send_request.return_value = mock_response(
        status=200, text=response_from_elemental_api)

    event_id = '999'
    client.describe_event(event_id)
    client.send_request.assert_called_once_with(
        http_method='GET',
        url=f'{ELEMENTAL_ADDRESS}/live_events/{event_id}',
        headers=HEADERS, timeout=None)


def test_describe_event_will_return_event_info_as_expect():
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)
    client.generate_headers = mock.Mock()
    client.generate_headers.return_value = HEADERS
    client.send_request = mock.Mock()
    response_from_elemental_api = file_fixture('sample_event.xml')
    client.send_request.return_value = mock_response(
        status=200, text=response_from_elemental_api)

    event_id = '139'
    event_info = client.describe_event(event_id)
    assert event_info == {'origin_url':
                          'https://vmjhch43nfkghi.data.mediastore.us-east-1.'
                          'amazonaws.com/mortyg3b4/master/mortyg3b4.m3u8',
                          'backup_url':
                          'https://vmjhch43nfkghi.data.mediastore.us-east-1.'
                          'amazonaws.com/mortyg3b4/backup/mortyg3b4.m3u8',
                          'status': 'complete'}


@pytest.mark.parametrize('status,expected_result', [
    ('pending', False),
    ('running', False),
    ('preprocessing', False),
    ('postprocessing', False),
    ('error', True),
    ('completed', True),
])
def test_event_can_delete(status, expected_result):
    client = ElementalLive(ELEMENTAL_ADDRESS, USER, API_KEY)

    client.describe_event = mock.Mock()
    client.describe_event.return_value = {
        'status': 'pending',
        'origin_url': 'fake_origin',
        'backup_url': 'fake_backup'
    }

    assert client.event_can_delete('123') is False
