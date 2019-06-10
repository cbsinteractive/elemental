import requests
from jinja2 import Template

xml_file = open("./templates/qvbr_mediastore.xml", 'r')
xml_content = xml_file.read()
template = Template(xml_content)
body = template.render(username = 'AKIAX3GU2745LBFI5NOH', password='AQbwCQuTXhfJH6KefbOYXSPL+SnlBITDi0zQG0bD',
                       mediastore_container='https://hu5n3jjiyi2jev.data.mediastore.us-east-1.amazonaws.com/c31/master')
print(body)


save = open('/Users/tmin0603/Desktop/working station/elemental/live/profile.xml','r')
s = save.read()
# print(s)


response = requests.post("http://elemental.dev.cbsivideo.com/live_events", data=s, headers={'Accept':'application/xml', 'Content-Type':'application/xml'})
print(response.text)
