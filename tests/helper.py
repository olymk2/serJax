import os
import pty
import json
import pytest
from contextlib import contextmanager
from serjax.server import app as app_test
from serjax.server import api, add_api_endpoints
from serjax.client import serial

add_api_endpoints(api)

@contextmanager
@pytest.fixture
def fetch_api_lock():
    """Context manager to setup and gain a lock on the serial port"""
    app = app_test.test_client()
    app.testing = True
    master_pty, slave_pty = pty.openpty()
    slave_port = os.ttyname(slave_pty)
    master_port = os.ttyname(master_pty)

    lock_response = app.get('/open')
    # assert lock_response.status_code == 201
    print(lock_response)
    print(lock_response.get_data())
    json_data = json.loads(lock_response.get_data().decode('ascii'))
    lock = str(json_data.get('api_lock', ''))
    yield (
        app,
        master_pty,
        slave_pty,
        master_port,
        slave_port,
        lock_response,
        lock)

    os.close(master_pty)
    os.close(slave_pty)
    app.get('/close')


class testSerial(serial):
    """override the client get and put methods for testing"""
    def __init__(self, url='', port=None):
        self.app = app_test.test_client()
        self.app.testing = True
        super(testSerial, self).__init__(url=url, port=port)

    def get(self, url):
        return json.loads(
            self.app.get(
                url,
                headers=self.headers
            ).get_data().decode('ascii')
        )

    def put(self, url, data=None):
        return json.loads(
            self.app.put(
                url,
                data=data,
                headers=self.headers
            ).get_data().decode('ascii')
        )

    def writelines(self, data):
        self.post('%s/write' % self.url, data={'data': data.read()})

    def post(self, url, data=None):
        return json.loads(
            self.app.put(
                url,
                data=data,
                headers=self.headers
            ).get_data().decode('ascii')
        )
