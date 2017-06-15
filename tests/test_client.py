import os
import pty
import json
from io import StringIO
from serjax.server import app
from serjax.client import serial
from tests.helper import fetch_api_lock


class testSerial(serial):
    """override the client get and put methods for testing"""
    def __init__(self, url='', port=None):
        self.app = app.test_client()
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


def test_complete_example():
    send_value1 = 'EHLO'
    send_value2 = 'Test value'

    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        print(mpty)
        print(spty)
        print(mport)
        print(sport)
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        with testSerial(port=sport) as sp:
            print('1')
            sp.write(send_value1)
            print('2')
            assert send_value1 == os.read(mpty, 1).decode('ascii')
            print('3')
#             sp.write(send_value2)
#             assert send_value2 == os.read(mpty, 1024).decode('ascii')


# def test_multiple_send():
#     send_values = StringIO(u"""
#         G0 X10.00\n
#         G0 X-10.00\n
#     """)

#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
#         with testSerial(port=sport) as sp:
#             sp.writelines(send_values)
#             send_values.seek(0)
#             assert send_values.read() == os.read(mpty, 1024).decode('ascii')

def test_is_connected():
    """Test that we can get an api_lock key"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        with testSerial(port=mport) as serial_port:
            serial_port.isConnected()

def test_in_waiting():
    """Test that we can get an api_lock key"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        with testSerial(port=mport) as serial_port:
            serial_port.inWaiting()

# def test_read():
#     """Test that we can get an api_lock key"""
#     text = b'long string'
#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         with testSerial(port=sport) as serial_port:
#             os.write(mpty, text)
#             assert text == serial_port.read()

def test_recv():
    """Test that we can get an api_lock key"""
    text = b'long string'
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        with testSerial(port=sport) as serial_port:
            os.write(mpty, text)
            #assert text, serial_port.recv())


def test_open_connection():
    """Test that we can get an api_lock key"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        with testSerial(port=sport) as sp1:
            sp1.read()
            with testSerial(port=mport) as sp2:
                sp2.read()
        #todo need to assert here

