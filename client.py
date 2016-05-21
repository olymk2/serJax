from requests import put, get, post


class serial(object):
    url = 'http://localhost:5005/'
    api_lock = ''
    headers = {}

    def __init__(self, url='', port=None):
        self.url = url        
        response = self.get('%s/open' % self.url)
        self.headers = {'api_lock': response.get('api_lock')}
        if port:
            self.open(port)

    def get(self, url):
        return get(url, headers = self.headers).json()

    def put(self, url, data=None):
        return put(url, data=data, headers = self.headers).json()

    def post(self, url, data=None):
        return post(url, data=data, headers = self.headers).json()

    def ports(self):
        ports = self.get('%s/ports' % (self.url)).json()
        return ports.keys()

    def open(self, port):
        response = self.put(
            '%s/open' % (self.url),
            data={'port': port})
        return response

    def __enter__(self):        
        return self

    def write(self, data):
        self.put('%s/write' % self.url, data={'data': data})

    def writelines(self, data):
        self.post('%s/write' % self.url, data={'data': data.read()})
    
    def read(self):
        result = self.get('%s/recv' % self.url)
        return result.get('data')
    
    def __exit__(self, type, value, traceback):
        self.api_lock = ''
        self.get('%s/close' % self.url)

