"""Client to connect to flask server"""
import requests
from requests.exceptions import ConnectionError
from serjax import ERROR_NOT_CONNECTED, ERROR_NO_ENDPOINT


class serial(object):
    url = 'http://localhost:5005/'
    api_lock = None
    headers = {}
    connected = False

    def __init__(self, url, port=None):
        if not url:
            return

        self.url = url

        if not port:
            return

        self.open(port)

    def get(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 201:
                return response.json()
        except ConnectionError:
            return {'status': ERROR_NOT_CONNECTED}
        result = response.json()
        result['status'] = ERROR_NO_ENDPOINT
        return result #{'status': ERROR_NO_ENDPOINT}

    def put(self, url, data=None):
        try:
            response = requests.put(url, data=data, headers=self.headers)
            print(self.headers)
            print(response.json())
            if response.status_code == 201:
                return response.json()
        except ConnectionError:
            return {'status': ERROR_NOT_CONNECTED}
        return {'status': ERROR_NO_ENDPOINT}

    def post(self, url, data=None):
        try:
            response = requests.post(url, data=data, headers=self.headers)
            if response.status_code == 201:
                return response.json()
        except ConnectionError:
            return {'status': ERROR_NOT_CONNECTED}
        return {'status': ERROR_NO_ENDPOINT}

    def isOpen(self):
        response = self.get('%s/status' % self.url)
        print(response)
        return True is response.get('connected', False)

    def inWaiting(self):
        response = self.get('%s/waiting' % self.url)
        return response.get('size', 0)

    def ports(self):
        ports = self.get('%s/ports' % (self.url))
        return ports.get('ports', '')

    def open(self, port):
        print(self.api_lock)
        if not self.api_lock:
            response = self.get('%s/open' % self.url)
            self.headers = {'api_lock': str(response.get('api_lock'))}
        response = self.put(
            '%s/open' % (self.url),
            data={'port': port})
        # self.headers = {'api_lock': response.get('api_lock', '')}
        return response

    def close(self):
        self.api_lock = None
        self.get('%s/close' % self.url)

    def __enter__(self):
        return self

    def write(self, data):
        response = self.put('%s/write' % self.url, data={'data': data})
        return response

    def writelines(self, data):
        self.post('%s/write' % self.url, data={'data': data.read()})

    def recv(self, length=1):
        result = self.get('%s/recv/%d' % (self.url, length))
        return result.get('data', '')

    # If nothing to read return None
    def read(self):
        result = self.get('%s/recv' % self.url)
        return result.get('data', '')

    def status(self):
        response = self.get('%s/status' % self.url)
        return response

    def __exit__(self, type, value, traceback):
        self.close()
