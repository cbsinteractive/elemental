import time
import hashlib
import requests
from jinja2 import Template



class ElementalLive():
    def __init__(self, server_ip):
        self.server_ip = server_ip


    # Simple version of generate_header, may need more paras in the future(like api_key)
    def generate_headers(self):
        return {
            'Accept': 'application/xml',
            'Content-Type': 'application/xml'
        }

    # General method to send request
    def send_request(self, method, querystring, data):
        result = None
        url = self.server_ip + 'live_events'
        if method == 'CREATE':
            result = requests.post(url, data=data, headers=self.generate_headers())
        elif method == 'DELETE':
            pass
        elif method == 'START':
            pass
        elif method == 'STOP':
            pass



        return result

    # Create event, options contain username, password and mediastore_container url
    def create_event(self, template_path, options):
        xml_file = open(template_path, 'r')
        xml_content = xml_file.read()
        template = Template(xml_content)

        # Pass paras to template
        body = template.render(**options)
        response = self.send_request('CREATE', None, body)
        return response

    def delete_event(self):
        pass

    def start_event(self):
        pass

    def stop_event(self):
        pass



