import time
import hashlib

from urllib.parse import urlparse


class ElementalLive():
    def __init__(self, server_ip):
        self.server_ip = server_ip

    def generate_headers(self, url, user, api_key):
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

    def send_request(self, method, path, querystring, data, headers):
        pass

    def create_event(self):
        pass

    def delete_event(self):
        pass

    def start_event(self):
        pass

    def stop_event(self):
        pass
