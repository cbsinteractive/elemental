import requests
from jinja2 import Template
import time
from urllib.parse import urlparse
import hashlib


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

        # Send request
        response = requests.request(method='POST', url=url, data=body,
                                    headers=headers)

        return response

    def delete_event(self, event_id):

        # Initial url
        url = f'{self.server_ip}/live_events/{event_id}'

        # Generate headers according to how users create ElementalLive class
        if self.user is None and self.api_key is None:
            headers = self.generate_header_with_authentication_disabled()
        else:
            headers = self.generate_headers_with_authentication_enabled(
                url, self.user, self.api_key)

        # Send request
        response = requests.request(method='DELETE', url=url,
                                    headers=headers)

        return response

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

        # Send request
        response = requests.request(method='POST', url=url, data=body,
                                    headers=headers)

        return response

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

        # Send request
        response = requests.request(method='POST', url=url, data=body,
                                    headers=headers)

        return response
