import os
import pty
import json
import pytest
from contextlib import contextmanager
from serjax.server import app as app_test


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

