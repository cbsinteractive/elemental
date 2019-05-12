from client import ElementalLive


def test_ElementalLive_should_receive_server_ip():
    e = ElementalLive('http://elemental-ip')
    assert e.server_ip == 'http://elemental-ip'
