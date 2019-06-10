from client import ElementalLive
from Keys import *
def test_ElementalLive_should_receive_server_ip():
    e = ElementalLive('http://elemental.dev.cbsivideo.com/')
    assert e.server_ip == 'http://elemental.dev.cbsivideo.com/'

def test_create_event_should_receive_201_status_code():
    eleClient = ElementalLive("http://elemental.dev.cbsivideo.com/")
    res = eleClient.create_event("./templates/qvbr_mediastore.xml",
                                 {'username': 'AKIAX3GU2745LBFI5NOH',
                                  'password': 'AQbwCQuTXhfJH6KefbOYXSPL+SnlBITDi0zQG0bD',
                                  'mediastore_container_master': 'https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/master',
                                  'mediastore_container_backup': 'https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/backup'})
    assert res.status_code == 201


