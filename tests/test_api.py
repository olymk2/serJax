import os
import pty
import json
from contextlib import contextmanager

from serjax.server import app as app_test
from tests.helper import fetch_api_lock


def test_open_port():
    """helper to get lock and open serial port"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        app.put('/open', data={'port': sport}, headers={'api_lock': lock})


def test_create_api_lock():
    """Test that we can get an api_lock key"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        assert len(lock) > 36
        assert rlock.status_code == 201


def test_open_non_existant_port():
    """testing opening a serial port that does not exist"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        # response = app.get('/close')
        response = app.put('/open', data={'port': '/dev/ttyNull'}, headers={'api_lock': lock})
        assert response.status_code == 404


def test_open_port_when_api_is_locked():
    """testing opening a serial port when the api is locked"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.get('/open')
        assert response.status_code == 404


def test_read_data():
    """test reading data from api"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        response = app.get('/recv', headers={'api_lock': lock})
        assert response.status_code == 201


def test_write_data():
    """test writting data to the api"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        send_data = u'ello'
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        response = app.put('/write', data={'data': send_data}, headers={'api_lock': lock})
        assert send_data == os.read(mpty, 1024).decode('ascii')
        assert response.status_code == 201


def test_write_data_buffered():
    """test writting data to the api"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        send_data = u"""
            ello 1\n
            ello 2\n
            ello 3\n
            ello 4\n"""
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        response = app.post('/write', data={'data': send_data}, headers={'api_lock': lock})
        assert send_data == os.read(mpty, 1024).decode('ascii')
        assert response.status_code == 201


def test_get_port_list():
    """Get a list of ports this can be done by anyone at any time no locking involved"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.get('/ports')
        assert response.status_code == 201


def test_status():
    """Get size in waiting"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        response = app.get('/status')
        assert response.status_code == 201


def test_in_waiting():
    """Get size in waiting"""
    with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
        response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
        # api_lock = open_port()
        response = app.get('/waiting',headers={'api_lock': lock})

        assert response.status_code == 201

        json_data = json.loads(response.get_data().decode('ascii'))
        assert json_data.get('size') == 0


# def test_history():
#     """Get size in waiting"""
#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
#         assert response.status_code == 201
#         # api_lock = open_port()
#         response = app.get('/history')
#         assert response.status_code == 201

#         json_data = json.loads(response.get_data().decode('ascii'))
#         assert json_data.get('data') == '[]'

#         response = app.put('/write', data={'data': 'command 1'}, headers={'api_lock': lock})
#         response = app.get('/history')
#         json_data = json.loads(response.get_data().decode('ascii'))
#         assert json_data.get('data') == '["write command 1"]'
#         assert response.status_code == 201
