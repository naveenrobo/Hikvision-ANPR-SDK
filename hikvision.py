import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import xmltodict

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import json


def response_parser(response, present='dict'):
    """ Convert Hikvision results
    """
    if isinstance(response, (list,)):
        result = "".join(response)
    else:
        result = response.text

    if present == 'dict':
        if isinstance(response, (list,)):
            events = []
            for event in response:
                e = json.loads(json.dumps(xmltodict.parse(event)))
                events.append(e)
            return events
        return json.loads(json.dumps(xmltodict.parse(result)))
    else:
        return result


class Client:

    def __init__(self, host, login=None, password=None, timeout=3, isapi_prefix='ISAPI'):
        self.host = host
        self.login = login
        self.password = password
        self.timeout = float(timeout)
        self.isapi_prefix = isapi_prefix
        self.req = self._check_session()
        self.count_events = 1

    def _check_session(self):
        """Check the connection with device

         :return request.session() object
        """
        full_url = urljoin(self.host, self.isapi_prefix + '/System/status')
        session = requests.session()
        session.auth = HTTPBasicAuth(self.login, self.password)
        response = session.get(full_url)
        if response.status_code == 401:
            session.auth = HTTPDigestAuth(self.login, self.password)
            response = session.get(full_url)
        response.raise_for_status()
        return session

    def getNumberPlates(self):
        payload = "<AfterTime><picTime>%s</picTime></AfterTime>".format("0")
        response = self.req.request(
            method='post', url="http://192.168.1.20/ISAPI/Traffic/channels/1/vehicleDetect/plates", timeout=self.timeout, stream=True, data=payload)
        return response


cam = Client('http://192.168.1.20', 'admin', 'Hik12345')


res = cam.getNumberPlates()

print(res.text)

print(response_parser(res))
