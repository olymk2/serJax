import os
from serjax.client import serial
from tests.helper import fetch_api_lock
from tests.helper import testSerial 


def test_send_values():
    # open psuedo pty serial port, send data with api and raw read its received
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        app.put('/open', data={'port': sport}, headers={'api_lock': lock})

        app.put('/write', data={'data': 'EHLO'}, headers={'api_lock': lock})
        assert 'EHLO' == os.read(mpty, 1024).decode('ascii')

        # second send
        app.put(
            '/write',
            data={'data': 'Random string'},
            headers={'api_lock': lock})
        assert 'Random string' == os.read(mpty, 1024).decode('ascii')


def test_read_values():
    # open psuedo pty serial port, send data with api and raw read its received
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        app.put('/open', data={'port': sport}, headers={'api_lock': lock})

        os.write(mpty, 'EHLO')
        response = app.put(
            '/read',
            headers={'api_lock': lock})
        assert 'EHLO' == os.read(mpty, 1024).decode('ascii')

        # second send
        response = app.put(
            '/read',
            headers={'api_lock': lock})
        assert 'Random string' == os.read(mpty, 1024).decode('ascii')



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

