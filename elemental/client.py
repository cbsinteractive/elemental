import hashlib
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
import xmltodict
from jinja2 import Template

TEMPLATE_PATH = "live/templates/qvbr_mediastore.xml"


class ElementalException(Exception):
    """Base exception for all exceptions ElementalLive client could raise"""
    pass


class InvalidRequest(ElementalException):
    """Exception raised by 'request' with invalid request"""
    pass


class InvalidResponse(ElementalException):
    """Exception raised by 'request' with invalid response"""
    pass


class ElementalLive():
    def __init__(self, server_ip, user=None, api_key=None):
        self.server_ip = server_ip
        self.user = user
        self.api_key = api_key

    def generate_headers(self, url=""):
        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            return {
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }
        else:
            expiration = int(time.time() + 120)
            parse = urlparse(url)
            prehash = "%s%s%s%s" % (
                parse.path, self.user, self.api_key, expiration)
            digest = hashlib.md5(prehash.encode('utf-8')).hexdigest()
            final_hash = "%s%s" % (self.api_key, digest)
            key = hashlib.md5(final_hash.encode('utf-8')).hexdigest()
            return {
                'X-Auth-User': self.user,
                'X-Auth-Expires': str(expiration),
                'X-Auth-Key': key,
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }

    def send_request(self, http_method, url, headers, body=""):
        # Send request according to different methods
        try:
            response = requests.request(
                method=http_method, url=url, data=body, headers=headers)

        except requests.exceptions.RequestException as e:
            raise InvalidRequest(f"{http_method}: {url} failed\n{e}")
        if response.status_code not in (200, 201):
            raise InvalidResponse(
                f"{http_method}: {url} failed\nResponse: "
                f"{response.status_code}\n{response.text}")
        return response

    def create_event(self, options):

        # Initiate url
        url = f'{self.server_ip}/live_events'

        # Generate template
        xml_file = open(TEMPLATE_PATH, 'r')
        xml_content = xml_file.read()
        xml_file.close()
        template = Template(xml_content)

        # Pass params to template
        body = template.render(**options)

        # Generate headers
        headers = self.generate_headers(url)

        # Send request and do exception handling
        response = self.send_request(
            http_method="POST", url=url, headers=headers, body=body)

        # Find newly created event id
        xml_root = ET.fromstring(response.content)
        ids = xml_root.findall('id')
        event_id = ids[0].text

        return {'id': event_id}

    def delete_event(self, event_id):

        # Initial url
        url = f'{self.server_ip}/live_events/{event_id}'

        # Generate headers
        headers = self.generate_headers(url)

        # Send request and do exception handling
        self.send_request(http_method="DELETE", url=url, headers=headers)

    def start_event(self, event_id):
        # Initail url
        url = f'{self.server_ip}/live_events/{event_id}/start'

        # Generate body
        body = "<start></start>"

        # Generate headers
        headers = self.generate_headers(url)

        # Send request and do exception handling
        self.send_request(http_method="POST", url=url,
                          headers=headers, body=body)

    def stop_event(self, event_id):
        # Initail url
        url = f'{self.server_ip}/live_events/{event_id}/stop'

        # Generate body
        body = "<stop></stop>"

        # Generate headers according to how users create ElementalLive class
        headers = self.generate_headers(url)

        # Send request and do exception handling
        self.send_request(http_method="POST", url=url,
                          headers=headers, body=body)

    def find_devices_in_use(self):
        events_url = f'{self.server_ip}/live_events?filter=active'
        events_headers = self.generate_headers(events_url)
        events_xml = self.send_request(
            http_method="GET", url=events_url, headers=events_headers)
        events_list = ET.fromstring(events_xml.text)

        # Find in use devices from active events
        in_use_devices = set()
        for device_name in events_list.iter('device_name'):
            in_use_devices.add(device_name.text)

        return in_use_devices

    def get_input_devices(self):
        devices_url = f'{self.server_ip}/devices'
        devices_headers = self.generate_headers(devices_url)
        devices_xml = self.send_request(
            http_method="GET", url=devices_url, headers=devices_headers)
        devices_info = xmltodict.parse(devices_xml.text)[
            'device_list']['device']

        devices_in_use = self.find_devices_in_use()

        for device in devices_info:
            device.pop('@href')
            device['availability'] = \
                (device['device_name'] not in devices_in_use)

        devices_info = sorted(
            devices_info, key=lambda d: int(d["id"]))
        return [dict(d) for d in devices_info]
