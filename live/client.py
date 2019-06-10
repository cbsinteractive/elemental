import time
import hashlib
import requests
from jinja2 import Template


from urllib.parse import urlparse



class ElementalLive():
    def __init__(self, server_ip):
        self.server_ip = server_ip

    # def generate_headers(self, url = None, user = None, api_key = None):
    #     expiration = int(time.time() + 120)
    #     parse = urlparse(url)
    #     prehash = "%s%s%s%s" % (parse.path, user, api_key, expiration)
    #     digest = hashlib.md5(prehash.encode('utf-8')).hexdigest()
    #     final_hash = "%s%s" % (api_key, digest)
    #     key = hashlib.md5(final_hash.encode('utf-8')).hexdigest()
    #     return {
    #         # 'X-Auth-User': user,
    #         # 'X-Auth-Expires': str(expiration),
    #         # 'X-Auth-Key': key,
    #         'Accept': 'application/xml',
    #         'Content-Type': 'application/xml'
    #     }

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
        body = template.render(username = options['username'], password = options['password'],
                               mediastore_container_master = options['mediastore_container_master'],
                               mediastore_container_backup = options['mediastore_container_backup'])
        response = self.send_request('CREATE', None, body)

        return response

    def delete_event(self):
        pass

    def start_event(self):
        pass

    def stop_event(self):
        pass

if __name__ == "__main__":
    eleClient = ElementalLive("http://elemental.dev.cbsivideo.com/")
    res = eleClient.create_event("./templates/qvbr_mediastore.xml",
                                 {'username': '***************', 'password' : '*****************',
                                  'mediastore_container_master' : 'https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/master',
                                  'mediastore_container_backup' : 'https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/backup'})
    print(res.status_code)
    # print(res.text)

