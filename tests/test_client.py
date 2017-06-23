from mock import patch
from serjax.client import serial
from serjax import ERROR_NOT_CONNECTED, ERROR_NO_ENDPOINT


def test_connection_to_invalid_url():
    with serial(url='http://localdoesnotexist:5005') as client:
        response = client.open('/dev/fakeport')
        assert response == {'status': ERROR_NOT_CONNECTED}


@patch('serjax.client.requests.put')
@patch('serjax.client.requests.get')
def test_port_list(mock_put, mock_get):
    mock_put.return_value.json.return_value = {
        'ports': ['/dev/tty0', '/dev/tty1']}
    mock_put.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        for port in client.ports():
            assert port.startswith('/dev/')


@patch('serjax.client.requests.get')
@patch('serjax.client.requests.put')
def test_open_port_values(mock_put, mock_get):
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = {'status': 'connected'}
        mock_put.return_value.status_code = 201
        response = client.open('/dev/faketty')
        assert response == {'status': 'connected'}

    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = {'status': ERROR_NO_ENDPOINT}
        mock_put.return_value.status_code = 404
        response = client.open('/dev/faketty')
        assert response == {'status': ERROR_NO_ENDPOINT}


@patch('serjax.client.requests.get')
@patch('serjax.client.requests.put')
def test_write_values(mock_put, mock_get):
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = "{'status': 'ok'}"
        mock_put.return_value.status_code = 201
        response = client.write('failed messaage')
        assert response == "{'status': 'ok'}"

    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = {'status': 'connected'}
        mock_put.return_value.status_code = 404
        response = client.write('failed messaage')
        assert response == {'status': ERROR_NO_ENDPOINT}


@patch('serjax.client.requests.get')
@patch('serjax.client.requests.put')
def test_read_values(mock_put, mock_get):
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_get.return_value.json.return_value = {'data': 'Read Value'}
        mock_get.return_value.status_code = 201
        response = client.read()
        assert response == 'Read Value'

    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_get.return_value.json.return_value = {'data': ''}
        mock_get.return_value.status_code = 404
        response = client.read()
        assert response == ''


@patch('serjax.client.requests.get')
def test_is_connected(mock_get):
    """Test that we can get an api_lock key"""
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_get.return_value.json.return_value = {'connected': True}
        mock_get.return_value.status_code = 201
        response = client.isOpen()
        assert response is True

    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_get.return_value.json.return_value = {'connected': False}
        mock_get.return_value.status_code = 404
        response = client.isOpen()
        assert response is False


@patch('serjax.client.requests.get')
@patch('serjax.client.requests.put')
def test_switch_port(mock_put, mock_get):
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = {'status': 'connected'}
        mock_put.return_value.status_code = 201
        response = client.open('/dev/faketty1')
        assert response == {'status': 'connected'}

        response = client.open('/dev/faketty2')
        assert response == {'status': 'connected'}


@patch('serjax.client.requests.get')
@patch('serjax.client.requests.put')
def test_in_waiting(mock_put, mock_get):
    """Test that we can get an api_lock key"""
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = {'status': 'connected'}
        mock_put.return_value.status_code = 201
        response = client.open('/dev/faketty1')

        mock_get.return_value.json.return_value = {'size': 0}
        mock_get.return_value.status_code = 201
        response = client.inWaiting()
        assert response == 0

        mock_get.return_value.json.return_value = {'size': len('EHLO')}
        mock_get.return_value.status_code = 201
        response = client.inWaiting()
        assert response == len('EHLO')


@patch('serjax.client.requests.get')
@patch('serjax.client.requests.put')
def test_open_connection(mock_put, mock_get):
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_put.return_value.json.return_value = {'status': 'connected'}
        mock_put.return_value.status_code = 201
        response = client.open('/dev/faketty1')
        assert response == {'status': 'connected'}

        mock_put.return_value.json.return_value = {'status': 'disconnected'}
        mock_put.return_value.status_code = 404
        response = client.open('/dev/faketty1')
        assert response == {'status': 3}
