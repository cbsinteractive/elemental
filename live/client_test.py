from client import ElementalLive
import mock
import os

def mock_response(status=200, content="CONTENT", json_data=None, raise_for_status=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()

    # mock raise_for_status call w/optional error
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status

    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content

    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp


def test_ElementalLive_should_receive_server_ip():
    e = ElementalLive('http://elemental.dev.cbsivideo.com/')
    assert e.server_ip == 'http://elemental.dev.cbsivideo.com/'


@mock.patch('requests.request')
def test_create_event_should_receive_201_status_code(mock_request):
    """test create_event method"""
    mock_resp = mock_response(status=201, content=open("./templates/sample_event.xml").read())
    mock_request.return_value = mock_resp

    client = ElementalLive("http://elemental.dev.cbsivideo.com/")
    res = client.create_event("./templates/qvbr_mediastore.xml",
                                 {'username': os.getenv('ACCESS_KEY'),
                                  'password': os.getenv('SECRET_KEY'),
                                  'mediastore_container_master': 'https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/master',
                                  'mediastore_container_backup': 'https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/backup'})
    assert res.status_code == 201


@mock.patch('requests.request')
def test_delete_event_should_receive_200_status_code(mock_request):
    """test delete_event method"""
    mock_resp = mock_response(status=200, content=open("./templates/sample_event.xml").read())
    mock_request.return_value = mock_resp

    client = ElementalLive("http://elemental.dev.cbsivideo.com/")
    res = client.delete_event(event_id=42)
    assert res.status_code == 200


@mock.patch('requests.request')
def test_start_event_should_receive_200_status_code(mock_request):
    """test start_event method"""
    mock_resp = mock_response(status=200, content=open("./templates/sample_event.xml").read())
    mock_request.return_value = mock_resp

    client = ElementalLive("http://elemental.dev.cbsivideo.com/")
    res = client.start_event(event_id=78)
    assert res.status_code == 200


@mock.patch('requests.request')
def test_stop_event_should_receive_200_status_code(mock_request):
    """test stop_event method"""
    mock_resp = mock_response(status=200, content=open("./templates/sample_event.xml").read())
    mock_request.return_value = mock_resp

    client = ElementalLive("http://elemental.dev.cbsivideo.com/")
    res = client.stop_event(event_id=78)
    assert res.status_code == 200







