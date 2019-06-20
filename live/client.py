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
            prehash = "%s%s%s%s" % (parse.path, self.user, self.api_key, expiration)
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


    def send_request(self, method, url, headers, body=""):
        # Default successful http status code
        right_status = 200

        # Send request according to different methods
        try:
            if method == "create":
                right_status = 201
                response = requests.request(method='POST', url=url, data=body,
                                            headers=headers)
            elif method == "delete":
                response = requests.request(method='DELETE', url=url, headers=headers)
            elif method == "start":
                response = requests.request(method='POST', url=url, data=body, headers=headers)
            else:
                response = requests.request(method='POST', url=url, data=body, headers=headers)

        except requests.exceptions.RequestException as e:
            raise InvalidRequestOrResponse(f"Fail to send request to {method} event\n{e}")
        if response.status_code != right_status:
            raise InvalidRequestOrResponse(f"Fail to {method} event\n"
                                           f"Response: "
                                           f"{response.status_code}\n{response.text}")
        return response

    def create_event(self, template_path, options):

        # Initiate url
        url = f'{self.server_ip}/live_events'

        # Generate template
        xml_file = open(template_path, 'r')
        xml_content = xml_file.read()
        template = Template(xml_content)

        # Pass params to template
        body = template.render(**options)

        # Generate headers
        headers = self.generate_headers(url)

        # Send request and do exception handling
        response = self.send_request("create", url, headers, body)

        # Find newly created event id
        xml_root = ET.fromstring(response.content)
        ids = xml_root.findall('id')
        event_id = ids[0].text

        return event_id

    def delete_event(self, event_id):

        # Initial url
        url = f'{self.server_ip}/live_events/{event_id}'

        # Generate headers
        headers = self.generate_headers(url)


        # Send request and do exception handling
        self.send_request("delete", url, headers)

        return

    def start_event(self, event_id):

        # Initail url
        url = f'{self.server_ip}/live_events/{event_id}/start'

        # Generate body
        body = "<start></start>"

        # Generate headers
        headers = self.generate_headers(url)

        # Send request and do exception handling
        self.send_request("start", url, headers, body)

        return

    def stop_event(self, event_id):

        # Initail url
        url = f'{self.server_ip}/live_events/{event_id}/stop'

        # Generate body
        body = "<stop></stop>"

        # Generate headers according to how users create ElementalLive class
        headers = self.generate_headers(url)

        # Send request and do exception handling
        self.send_request("stop", url, headers, body)

        return
