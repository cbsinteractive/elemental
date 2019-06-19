import requests
from jinja2 import Template
import time
from urllib.parse import urlparse
import hashlib
import xml.etree.ElementTree as ET

class ElementalException(Exception):
    """Base exception for all exceptions ElementalLive client could raise"""
    pass

class InvalidRequestOrResponse(ElementalException):
    """Exception raised by 'request' with invalid request or response"""
    pass

# def send_request_with_exception_handling(http_method, url, headers, body=""):
#     try:
#         response = requests.request(method=http_method, url=url, data=body,
#                                     headers=headers)
#         # Send request and do exception handling
#         if http_method == 'DELETE':
#             method = 'delete'
#         elif body == "<start></start>":
#             method = 'start'
#         elif body == '<stop></stop>':
#             method = 'stop'
#         else:
#             method = 'create'
#             # Find newly created event id
#             xml_root = ET.fromstring(response.content)
#             ids = xml_root.findall('id')
#             event_id = ids[0].text
#
#     except requests.exceptions.RequestException as e:
#         raise InvalidRequestOrResponse(f"Fail to send request to {method} event\n{e}")
#     if response.status_code != 201:
#         raise InvalidRequestOrResponse(f"Fail to {method} event\n"
#                                        f"Response: "
#                                        f"{response.status_code}\n{response.text}")
#     return event_id

class ElementalLive():
    def __init__(self, server_ip, user=None, api_key=None):
        self.server_ip = server_ip
        self.user = user
        self.api_key = api_key

    def generate_headers_with_authentication_enabled(self, url, user, api_key):
        expiration = int(time.time() + 120)
        parse = urlparse(url)
        prehash = "%s%s%s%s" % (parse.path, user, api_key, expiration)
        digest = hashlib.md5(prehash.encode('utf-8')).hexdigest()
        final_hash = "%s%s" % (api_key, digest)
        key = hashlib.md5(final_hash.encode('utf-8')).hexdigest()
        return {
            'X-Auth-User': user,
            'X-Auth-Expires': str(expiration),
            'X-Auth-Key': key,
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

    def generate_header_with_authentication_disabled(self):
        return {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

    def create_event(self, template_path, options):

        # Initiate url
        url = f'{self.server_ip}/live_events'

        # Generate template
        xml_file = open(template_path, 'r')
        xml_content = xml_file.read()
        template = Template(xml_content)

        # Pass params to template
        body = template.render(**options)

        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            headers = self.generate_header_with_authentication_disabled()
        else:
            headers = self.generate_headers_with_authentication_enabled(
                url, self.user, self.api_key)

        # Send request and do exception handling
        try:
            response = requests.request(method='POST', url=url, data=body,
                                        headers=headers)
        except requests.exceptions.RequestException as e:
            raise InvalidRequestOrResponse(f"Fail to send request to create event\n{e}")
        if response.status_code != 201:
            raise InvalidRequestOrResponse(f"Fail to create event\n"
                                           f"Response: "
                                           f"{response.status_code}\n{response.text}")

        # Find newly created event id
        xml_root = ET.fromstring(response.content)
        ids = xml_root.findall('id')
        event_id = ids[0].text

        return event_id

    def delete_event(self, event_id):

        # Initial url
        url = f'{self.server_ip}/live_events/{event_id}'

        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            headers = self.generate_header_with_authentication_disabled()
        else:
            headers = self.generate_headers_with_authentication_enabled(
                url, self.user, self.api_key)

        # Send request and do exception handling
        try:
            response = requests.request(method='DELETE', url=url,
                                        headers=headers, data="<start></start>")
        except requests.exceptions.RequestException as e:
            raise InvalidRequestOrResponse(f"Fail to send request to delete event\n{e}")
        if response.status_code != 200:
            raise InvalidRequestOrResponse(f"Fail to delete event with id: {event_id}\n"
                                           f"Response: "
                                           f"{response.status_code}\n{response.text}")

        return

    def start_event(self, event_id):

        # Initail url
        url = f'{self.server_ip}/live_events/{event_id}/start'

        # Generate body
        body = "<start></start>"

        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            headers = self.generate_header_with_authentication_disabled()
        else:
            headers = self.generate_headers_with_authentication_enabled(
                url, self.user, self.api_key)

        # Send request and do exception handling
        try:
            response = requests.request(method='POST', url=url, data=body,
                                        headers=headers)
        except requests.exceptions.RequestException as e:
            raise InvalidRequestOrResponse(f"Fail to send request to start event\n{e}")
        if response.status_code != 200:
            raise InvalidRequestOrResponse(f"Fail to start event with id: {event_id}\n"
                                           f"Response: "
                                           f"{response.status_code}\n{response.text}")

        return

    def stop_event(self, event_id):

        # Initail url
        url = f'{self.server_ip}/live_events/{event_id}/stop'

        # Generate body
        body = "<stop></stop>"

        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            headers = self.generate_header_with_authentication_disabled()
        else:
            headers = self.generate_headers_with_authentication_enabled(
                url, self.user, self.api_key)

        # Send request and do exception handling
        try:
            response = requests.request(method='POST', url=url, data=body,
                                        headers=headers)
        except requests.exceptions.RequestException as e:
            raise InvalidRequestOrResponse(f"Fail to send request to stop event\n{e}")
        if response.status_code != 200:
            raise InvalidRequestOrResponse(f"Fail to stop event with id: {event_id}\n"
                                           f"Response: "
                                           f"{response.status_code}\n{response.text}")

        return
