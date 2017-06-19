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
            print(port)
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
        mock_get.return_value.json.return_value = {'data': 'read_value'}
        mock_get.return_value.status_code = 404
        response = client.read()
        assert response == None


@patch('serjax.client.requests.get')
def test_is_connected(mock_get):
    """Test that we can get an api_lock key"""
    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_get.return_value.json.return_value = {'connected': 'True'}
        mock_get.return_value.status_code = 201
        response = client.isConnected()
        assert response == True

    mock_get.return_value.json.return_value = {'api_lock': '12345'}
    mock_get.return_value.status_code = 201
    with serial(url='http://localhost:5005') as client:
        mock_get.return_value.json.return_value = {'connected': 'False'}
        mock_get.return_value.status_code = 404
        response = client.isConnected()
        assert response == False

# def test_in_waiting():
#     """Test that we can get an api_lock key"""
#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
#         with testSerial(port=mport) as serial_port:
#             serial_port.inWaiting()

# def test_read():
#     """Test that we can get an api_lock key"""
#     text = b'long string'
#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         with testSerial(port=sport) as serial_port:
#             os.write(mpty, text)
#             assert text == serial_port.read()

# def test_recv():
#     """Test that we can get an api_lock key"""
#     text = b'long string'
#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
#         with testSerial(port=sport) as serial_port:
#             os.write(mpty, text)
#             #assert text, serial_port.recv())


# def test_open_connection():
#     """Test that we can get an api_lock key"""
#     with fetch_api_lock() as (app, mpty, spty, mport, sport, rlock, lock):
#         response = app.put('/open', data={'port': sport}, headers={'api_lock': lock})
#         with testSerial(port=sport) as sp1:
#             sp1.read()
#             with testSerial(port=mport) as sp2:
#                 sp2.read()
#         #todo need to assert here

