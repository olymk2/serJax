"""Client to connect to flask server"""
import requests


class serial(object):
    url = 'http://localhost:5005/'
    api_lock = ''
    headers = {}

    def __init__(self, url, port=None):
        self.url = url
        response = self.get('%s/open' % self.url)
        self.headers = {'api_lock': str(response.get('api_lock'))}
        if port:
            self.open(port)

    def get(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        return {'status': 'error'}

    def put(self, url, data=None):
        response = requests.put(url, data=data, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        return "{'status': 'error'}"

    def post(self, url, data=None):
        response = requests.post(url, data=data, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        return "{'status': 'error'}"

    def isConnected(self):
        response = self.get('%s/status' % self.url)
        return 'true' == response.get('connected', '').lower()

    def inWaiting(self):
        response = self.get('%s/waiting' % self.url)
        return response.get('size', 0)

    def ports(self):
        ports = self.get('%s/ports' % (self.url)).json()
        return ports.keys()

    def open(self, port):
        response = self.put(
            '%s/open' % (self.url),
            data={'port': port})
        return response

    def close(self):
        self.api_lock = ''
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
        return result.get('data')

    # If nothing to read return None
    def read(self):
        result = self.get('%s/recv' % self.url)
        return result.get('data')

    def status(self):
        response = self.get('%s/status' % self.url)
        return response

    def __exit__(self, type, value, traceback):
        self.close()
