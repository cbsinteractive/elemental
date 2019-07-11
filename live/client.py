import hashlib
import json
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import requests
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


def etree_to_dict(tree_node):
    dic = {}
    children = tree_node.getchildren()
    if children != []:
        dic[tree_node.tag] = {}
        for sub_node in children:
            dic[tree_node.tag][sub_node.tag] = list(
                etree_to_dict(sub_node).values())[0]
    else:
        dic[tree_node.tag] = tree_node.text
    return dic


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

    def get_input_devices(self):
        events_url = f'{self.server_ip}/live_events'
        events_headers = self.generate_headers(events_url)
        events_xml = self.send_request(
            http_method="GET", url=events_url, headers=events_headers)
        # print("8**********", events_xml.text)
        devices_url = f'{self.server_ip}/devices'
        devices_headers = self.generate_headers(devices_url)
        devices_xml = self.send_request(
            http_method="GET", url=devices_url, headers=devices_headers)
        # print("7**********", devices_xml.text)

        events_list = ET.fromstring(events_xml.text)
        devices_list = ET.fromstring(devices_xml.text)

        # with open('events.html', 'w') as file:
        #     file.write(events_xml.text)

        # Find all devices info
        devices_info = []
        all_devices = set()
        for device in devices_list:
            all_devices.add(device.find('device_name').text)
            device_dic = etree_to_dict(device)
            devices_info.append(device_dic['device'])

        # Find in use devices from all events
        in_use_devices = set()
        for event in events_list:
            status = event.find('status').text
            for input in event.findall('input'):
                device_input = input.find('device_input')
                if device_input:
                    device_name = device_input.find('device_name')
                    if status == 'preprocessing' or status == 'running':
                        in_use_devices.add(device_name.text)

        devices_availability = {}

        for d in all_devices:
            devices_availability[d] = True
        for d in in_use_devices:
            devices_availability[d] = False

        # Append availability info to device info
        for device in devices_info:
            device['availability'] = devices_availability[device['device_name']]

        devices_info = sorted(devices_info, key=lambda a: int(a["id"]))
        print(json.dumps(devices_info))
        return json.dumps(devices_info)
