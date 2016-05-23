import os
import sys
import pty
import json
import unittest

from io import StringIO
sys.path.append(os.path.abspath('../'))

from server import app
from client import serial

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
                headers = self.headers
            ).get_data().decode('ascii')
        )

    def put(self, url, data=None):
        return json.loads(
            self.app.put(
                url,
                data=data,
                headers = self.headers
            ).get_data().decode('ascii')
        )

    def post(self, url, data=None):
        return json.loads(
            self.app.put(
                url,
                data=data,
                headers = self.headers
            ).get_data().decode('ascii')
        )


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        """Create instance of app and a serial port to use"""
        self.master_pty, self.slave_pty = pty.openpty()
        self.slave_port = os.ttyname(self.slave_pty)
        self.master_port = os.ttyname(self.master_pty)

    def doCleanups(self):
        """close the psuedo ttys and release the lock"""
        os.close(self.master_pty)
        os.close(self.slave_pty)

    def test_complete_example(self):
        send_value1 = 'EHLO'
        send_value2 = 'Test value'
        with testSerial(port=self.slave_port) as sp:
            sp.write(send_value1)
            self.assertEqual(send_value1, os.read(self.master_pty, 1024).decode('ascii'))
            sp.write(send_value2)
            self.assertEqual(send_value2, os.read(self.master_pty, 1024).decode('ascii'))

    def test_multiple_send(self):
        send_values = StringIO(u"""
            G0 X10.00\n
            G0 X-10.00\n
        """)

        with testSerial(port=self.slave_port) as sp:
            sp.writelines(send_values)
            send_values.seek(0)
            self.assertEqual(send_values.read(), os.read(self.master_pty, 1024).decode('ascii'))

    def test_is_connected(self):
        """Test that we can get an api_lock key"""
        with testSerial(port=self.master_port) as serial_port:
            serial_port.isConnected();

    def test_in_waiting(self):
        """Test that we can get an api_lock key"""
        with testSerial(port=self.master_port) as serial_port:
            serial_port.inWaiting();

    def test_open_connection(self):
        """Test that we can get an api_lock key"""
        with testSerial(port=self.master_port) as sp1:
            sp1.read()
            with testSerial(port=self.master_port) as sp2:
                sp2.read()
        #todo need to assert here

if __name__ == '__main__':
    unittest.main()
