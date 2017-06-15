import os
import pty
import json
import unittest
from contextlib import contextmanager

from serjax.server import app


class ApiHelper:
    def __enter__(self):
        self.app = app.test_client()
        self.app.testing = True
        self.master_pty, self.slave_pty = pty.openpty()
        self.slave_port = os.ttyname(self.slave_pty)
        self.master_port = os.ttyname(self.master_pty)
        return self.app, self.master_pty, self.slave_pty

    def __exit__(self, type, value, traceback):
        os.close(self.master_pty)
        os.close(self.slave_pty)
        self.app.get('/close')

@contextmanager
def api_helper(app, master_pty, slave_pty):
    app = app.test_client()
    app.testing = True
    master_pty, slave_pty = pty.openpty()
    slave_port = os.ttyname(slave_pty)
    master_port = os.ttyname(master_pty)
    yield app, master_pty, slave_pty
    os.close(master_pty)
    os.close(slave_pty)
    app.get('/close')



def test_fetch_api_lock(app, mpty, spty):
    with api_helper as app, mpty, spty:
        response = app.get('/open')
        json_data = json.loads(response.get_data().decode('ascii'))
        return str(json_data.get('api_lock', ''))


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        """Create instance of app and a serial port to use"""
        self.app = app.test_client()
        self.app.testing = True
        self.master_pty, self.slave_pty = pty.openpty()
        self.slave_port = os.ttyname(self.slave_pty)
        self.master_port = os.ttyname(self.master_pty)

    def doCleanups(self):
        """close the psuedo ttys and release the lock"""
        os.close(self.master_pty)
        os.close(self.slave_pty)
        self.app.get('/close')

    def get_api_lock(self):
        """helper to get a lok on the api"""
        response = self.app.get('/open')
        json_data = json.loads(response.get_data().decode('ascii'))
        return str(json_data.get('api_lock', ''))

    def open_port(self):
        """helper to get lock and open serial port"""
        api_lock = self.get_api_lock()
        self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        return api_lock

    def test_create_api_lock(self):
        """Test that we can get an api_lock key"""
        response = self.app.get('/open')
        json_data = json.loads(response.get_data().decode('ascii'))
        length = len(str(json_data.get('api_lock', '')))
        self.assertGreaterEqual(length, 37)
        self.assertEqual(response.status_code, 201)

    def test_open_non_existant_port(self):
        api_lock = self.get_api_lock()
        """testing opening a serial port that does not exist"""
        response = self.app.put('/open', data={'port': '/dev/ttyNull'}, headers={'api_lock': api_lock})
        self.assertEqual(response.status_code, 404)

    def test_open_port_when_api_is_locked(self):
        """testing opening a serial port when the api is locked"""
        response = self.app.get('/open')
        response = self.app.get('/open')
        self.assertEqual(response.status_code, 404)

    def test_read_data(self):
        """test reading data from api"""
        api_lock = self.get_api_lock()
        response = self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        response = self.app.get('/recv', headers={'api_lock': api_lock})
        self.assertEqual(response.status_code, 201)

    def test_write_data(self):
        """test writting data to the api"""
        send_data = u'ello'
        api_lock = self.get_api_lock()
        response = self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        response = self.app.put('/write', data={'data': send_data}, headers={'api_lock': api_lock})
        self.assertEqual(send_data, os.read(self.master_pty, 1024).decode('ascii'))
        self.assertEqual(response.status_code, 201)

    def test_write_data_buffered(self):
        """test writting data to the api"""
        send_data = u"""
            ello 1\n
            ello 2\n
            ello 3\n
            ello 4\n"""
        api_lock = self.get_api_lock()
        response = self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        response = self.app.post('/write', data={'data': send_data}, headers={'api_lock': api_lock})
        self.assertEqual(send_data, os.read(self.master_pty, 1024).decode('ascii'))
        self.assertEqual(response.status_code, 201)

    def test_get_port_list(self):
        """Get a list of ports this can be done by anyone at any time no locking involved"""
        response = self.app.get('/ports')
        self.assertEqual(response.status_code, 201)

    def test_status(self):
        """Get size in waiting"""
        self.open_port()
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 201)

    def test_in_waiting(self):
        """Get size in waiting"""
        api_lock = self.open_port()
        response = self.app.get('/waiting',headers={'api_lock': api_lock})

        self.assertEqual(response.status_code, 201)

        json_data = json.loads(response.get_data().decode('ascii'))
        self.assertEqual(json_data.get('size'), 0)

    def test_history(self):
        """Get size in waiting"""
        api_lock = self.open_port()
        response = self.app.get('/history')
        self.assertEqual(response.status_code, 201)

        json_data = json.loads(response.get_data().decode('ascii'))
        self.assertEqual(json_data.get('data'), '[]')

        response = self.app.put('/write', data={'data': 'command 1'}, headers={'api_lock': api_lock})
        response = self.app.get('/history')
        json_data = json.loads(response.get_data().decode('ascii'))
        self.assertEqual(json_data.get('data'), '["write command 1"]')
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
