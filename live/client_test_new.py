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


def test_generate_header_with_authentication():
    """"test generate function"""
    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)
    headers = client.generate_headers("http://elemental.dev.cbsivideo.com/live_events")
    assert headers['X-Auth-User'] == USER
    assert headers['Accept'] == 'application/xml'
    assert headers['Content-Type'] == 'application/xml'

def test_genterate_header_without_authentication():
    """"test generate function"""
    client = ElementalLive("http://elemental.dev.cbsivideo.com")
    headers = client.generate_headers()
    assert headers['Accept'] == 'application/xml'
    assert headers['Content-Type'] == 'application/xml'

@mock.patch('requests.request')
def test_send_request_to_create_event(mock_request):
    """test create_event method"""
    response_from_elemental_api = open(
        'live/templates/sample_response_for_create.xml').read()
    mock_request.return_value = mock_response(
        status=201, content=response_from_elemental_api)

    client = ElementalLive("http://elemental.dev.cbsivideo.com", USER, API_KEY)
    event_id = client.send_request('create', "http://elemental.dev.cbsivideo.com/live_events", )

    request_to_elemental = mock_request.call_args_list[0][1]
    assert request_to_elemental['url'] == 'http://elemental' \
                                          '.dev.cbsivideo.com/live_events'
    assert request_to_elemental['method'] == 'POST'
    assert request_to_elemental['headers']['Accept'] == 'application/xml'
    assert request_to_elemental['headers']['Content-Type'] == 'application/xml'
    assert event_id == "80"

