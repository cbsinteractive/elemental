import ast
import hashlib
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, TypedDict
from urllib.parse import urlparse

import requests
import xmltodict  # type: ignore


class ElementalException(Exception):
    """Base exception for all exceptions ElementalLive client could raise"""
    pass


class InvalidRequest(ElementalException):
    """Exception raised by 'request' with invalid request"""
    pass


class InvalidResponse(ElementalException):
    """Exception raised by 'request' with invalid response"""
    pass


EventIdDict = TypedDict('EventIdDict', {'id': str})

EventStatusDict = TypedDict('EventStatusDict', {'origin_url': str, 'backup_url': Optional[str], 'status': str})

DeviceAvailabilityDict = TypedDict('DeviceAvailabilityDict', {
    'id': str,
    'name': Optional[str],
    'device_name': str,
    'device_number': str,
    'device_type': str,
    'description': str,
    'channel': str,
    'channel_type': str,
    'quad': str,
    'availability': bool
})

PreviewUrlDict = TypedDict('PreviewUrlDict', {'preview_url': str})


class ElementalLive:
    def __init__(self, server_url: str, user: Optional[str] = None, api_key: Optional[str] = None,
                 timeout: Optional[int] = 5) -> None:
        self.server_url = server_url
        self.user = user
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def generate_headers(self, url: Optional[str] = "") -> Dict[str, str]:
        # Generate headers according to how users create ElementalLive class
        if self.user is None or self.api_key is None:
            return {
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }
        else:
            expiration = int(time.time() + 120)
            parse = urlparse(url)
            pre_hash = f"{str(parse.path)}{self.user}{self.api_key}{expiration}"
            digest = hashlib.md5(pre_hash.encode('utf-8')).hexdigest()
            final_hash = f"{self.api_key}{digest}"
            key = hashlib.md5(final_hash.encode('utf-8')).hexdigest()

            return {
                'X-Auth-User': str(self.user),
                'X-Auth-Expires': str(expiration),
                'X-Auth-Key': key,
                'Accept': 'application/xml',
                'Content-Type': 'application/xml'
            }

    def send_request(self, http_method: str, url: str, headers: Dict[str, str],
                     body: Optional[str] = "", timeout: Optional[int] = None) -> requests.Response:
        # Send request according to different methods
        try:
            timeout = timeout or self.timeout
            response = self.session.request(
                method=http_method, url=url, data=body, headers=headers, timeout=timeout)

        except requests.exceptions.RequestException as e:
            raise InvalidRequest(f"{http_method}: {url} failed\n{e}")
        if response.status_code not in (200, 201):
            raise InvalidResponse(
                f"{http_method}: {url} failed\nResponse: "
                f"{response.status_code}\n{response.text}")
        return response

    def create_event(self, event_xml: str, timeout: Optional[int] = None) -> EventIdDict:
        url = f'{self.server_url}/live_events'
        headers = self.generate_headers(url)
        response = self.send_request(
            http_method="POST", url=url, headers=headers, body=event_xml, timeout=timeout)
        xml_root = ET.fromstring(response.content)
        ids = xml_root.findall('id')
        event_id = str(ids[0].text)

        return {'id': event_id}

    def update_event(self, event_id: str, event_xml: str, restart: Optional[bool] = False,
                     timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}'
        if restart:
            url += '?unlocked=1'
        headers = self.generate_headers(url)
        self.send_request(
            http_method="PUT", url=url, headers=headers, body=event_xml, timeout=timeout)

    def delete_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}'
        headers = self.generate_headers(url)
        self.send_request(http_method="DELETE", url=url, headers=headers, timeout=timeout)

    def cancel_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/cancel'
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, timeout=timeout)

    def start_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/start'
        body = "<start></start>"
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, body=body, timeout=timeout)

    def stop_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/stop'
        body = "<stop></stop>"
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, body=body, timeout=timeout)

    def reset_event(self, event_id: str, timeout: Optional[int] = None) -> None:
        url = f'{self.server_url}/live_events/{event_id}/reset'
        headers = self.generate_headers(url)
        self.send_request(http_method="POST", url=url, headers=headers, body="", timeout=timeout)

    def describe_event(self, event_id: str, timeout: Optional[int] = None) -> EventStatusDict:
        url = f'{self.server_url}/live_events/{event_id}'
        headers = self.generate_headers(url)
        response = self.send_request(http_method="GET", url=url,
                                     headers=headers, timeout=timeout)
        event_info = {}

        destinations = list(ET.fromstring(response.text).iter('destination'))
        uri = destinations[0].find('uri')
        event_info['origin_url'] = uri.text if uri is not None else ''
        if len(destinations) > 1:
            uri = destinations[1].find('uri')
            event_info['backup_url'] = uri.text if uri is not None else ''

        event_info['status'] = self._parse_status(response.text)

        return EventStatusDict(
            status=str(event_info['status']),
            origin_url=str(event_info['origin_url']),
            backup_url=event_info.get('backup_url')
        )

    def get_event_status(self, event_id: str, timeout: Optional[int] = None) -> str:
        url = f'{self.server_url}/live_events/{event_id}/status'
        headers = self.generate_headers(url)
        response = self.send_request(http_method="GET", url=url, headers=headers, timeout=timeout)
        return self._parse_status(response.text)

    def find_devices_in_use(self, timeout: Optional[int] = None) -> Set[Optional[str]]:
        events_url = f'{self.server_url}/live_events?filter=active'
        events_headers = self.generate_headers(events_url)
        events = self.send_request(
            http_method="GET", url=events_url, headers=events_headers, timeout=timeout)
        events_list = ET.fromstring(events.text)

        # Find in use devices from active events
        in_use_devices = set()
        for device_name in events_list.iter('device_name'):
            in_use_devices.add(device_name.text)

        return in_use_devices

    def get_input_devices(self, timeout: Optional[int] = None) -> List[DeviceAvailabilityDict]:
        devices_url = f'{self.server_url}/devices'
        devices_headers = self.generate_headers(devices_url)
        devices = self.send_request(
            http_method="GET", url=devices_url, headers=devices_headers, timeout=timeout)
        devices_information = xmltodict.parse(devices.text)[
            'device_list']['device']

        devices_in_use = self.find_devices_in_use()

        for device in devices_information:
            device.pop('@href')
            device['availability'] = \
                (device['device_name'] not in devices_in_use)

        devices_information = sorted(devices_information, key=lambda d: int(d["id"]))
        return [DeviceAvailabilityDict(
            id=device_info['id'],
            name=device_info['name'],
            description=device_info['description'],
            device_name=device_info['device_name'],
            device_number=device_info['device_number'],
            device_type=device_info['device_type'],
            availability=device_info['availability'],
            channel=device_info['channel'],
            channel_type=device_info['channel_type'],
            quad=device_info['quad'],
        ) for device_info in devices_information]

    def get_input_device_by_id(self, input_device_id: str, timeout: Optional[int] = None) -> DeviceAvailabilityDict:
        devices_url = f'{self.server_url}/devices/{input_device_id}'
        devices_headers = self.generate_headers(devices_url)
        devices = self.send_request(
            http_method="GET", url=devices_url, headers=devices_headers, timeout=timeout)
        device_info = xmltodict.parse(devices.text)['device']
        devices_in_use = self.find_devices_in_use()
        device_info['availability'] = (device_info['device_name']
                                       not in devices_in_use)
        device_info.pop('@href')
        return DeviceAvailabilityDict(
            id=device_info['id'],
            name=device_info['name'],
            description=device_info['description'],
            device_name=device_info['device_name'],
            device_number=device_info['device_number'],
            device_type=device_info['device_type'],
            availability=device_info['availability'],
            channel=device_info['channel'],
            channel_type=device_info['channel_type'],
            quad=device_info['quad'],
        )

    def generate_preview(self, input_id: str, timeout: Optional[int] = None) -> PreviewUrlDict:
        url = f'{self.server_url}/inputs/generate_preview'
        headers = self.generate_headers(url)

        headers['Accept'] = '*/*'
        headers['Content-Type'] = 'application/x-www-form-urlencoded; ' \
                                  'charset=UTF-8'

        # generate body
        data = f"input_key=0&live_event[inputs_attributes][0][source_type]=" \
               f"DeviceInput&live_event[inputs_attributes][0]" \
               f"[device_input_attributes][sdi_settings_attributes]" \
               f"[input_format]=Auto&live_event[inputs_attributes][0]" \
               f"[device_input_attributes][device_id]={input_id}"
        response = self.send_request(
            http_method="POST", url=url, headers=headers, body=data, timeout=timeout)

        response_parse = ast.literal_eval(response.text)

        if 'type' in response_parse and response_parse['type'] == 'error':
            raise ElementalException(
                f"Response: {response.status_code}\n{response.text}")
        else:
            preview_url = f'{self.server_url}/images/thumbs/' \
                          f'p_{response_parse["preview_image_id"]}_job_0.jpg'
            return {'preview_url': preview_url}

    def event_can_delete(self, channel_id: str, timeout: Optional[int] = None) -> bool:
        channel_info = self.describe_event(channel_id, timeout=timeout)
        return channel_info['status'] not in ('pending', 'running', 'preprocessing', 'postprocessing',)

    def _parse_status(self, text):
        status = ET.fromstring(text).find('status')
        return status.text if status is not None else 'unknown'
