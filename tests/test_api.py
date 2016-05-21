import os
import sys
import pty
import json
import unittest

sys.path.append(os.path.abspath('../'))

from server import app


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
        json_data = json.loads(response.get_data())
        return str(json_data.get('api_lock', ''))

    def open_port(self):
        """helper to get lock and open serial port"""
        api_lock = self.get_api_lock()
        self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        return api_lock

    def test_create_api_lock(self):
        """Test that we can get an api_lock key"""
        response = self.app.get('/open')
        json_data = json.loads(response.get_data())
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
        send_data = 'ello'
        api_lock = self.get_api_lock()
        response = self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        response = self.app.put('/write', data={'data': send_data}, headers={'api_lock': api_lock})
        self.assertEqual(send_data + '\r\n', os.read(self.master_pty, 1024))
        self.assertEqual(response.status_code, 201)

    def test_write_data_buffered(self):
        """test writting data to the api"""
        send_data = 'ello'
        api_lock = self.get_api_lock()
        response = self.app.put('/open', data={'port': self.slave_port}, headers={'api_lock': api_lock})
        response = self.app.post('/write', data={'data': send_data}, headers={'api_lock': api_lock})
        self.assertEqual(send_data + '\r\n', os.read(self.master_pty, 1024))
        self.assertEqual(response.status_code, 201)

    def test_get_port_list(self):
        """Get a list of ports this can be done by anyone at any time no locking involved"""
        response = self.app.get('/ports')
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
