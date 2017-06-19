#!/usr/bin/python
# -*- coding: utf-8 -*-
__version__ = '0.1.1'

import json
import urllib
import random
import logging
from io import StringIO

from collections import deque
from flask import Flask
from flask import request
from flask_restful import reqparse, abort, Api, Resource

from serjax.connect import serialPort


logging.basicConfig(level=logging.DEBUG)
serial_lock = None
history = deque(maxlen=100)
printer = serialPort()
root_url = 'http://127.0.0.1:5005/'

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()


def api_lock(func):
    """decorator to check if api is available will raise a 404 if locked"""
    def func_wrapper(name):
        request_lock = request.headers.get('api_lock')

        if request_lock is None:
            return abort(
                404, message='You do not have a lock on this resource')

        if str(serial_lock) == str(request_lock):
            return func(name)

        return abort(
            404, message='Api locked by another user')
    return func_wrapper


def connected(func):
    """decorator to test if the serial port is opened"""
    def func_wrapper(name):
        if printer.connected is False:
            return abort(404, message='Not connected to a device')
        return func(name)
    return func_wrapper


class Connection(Resource):
    def get(self):
        global serial_lock
        if serial_lock is not None:
            return abort(404, message='Serial port in use')
        serial_lock = str(random.getrandbits(128))
        return {'api_lock': serial_lock}, 201

    @api_lock
    def put(self):
        global serial_lock
        port = request.form.get('port', '')
        if not port:
            return abort(404, message='Invalid port')

        printer.connect(port)

        if printer.isConnected() is True:
            return {'status': 'connected'}, 201
        return abort(404, message='not connected')


class ClosePort(Resource):
    def get(self):
        global serial_lock
        printer.close()
        serial_lock = None
        return {'status': 'closed'}, 201


class Help(Resource):
    def get(self):
        """Print available functions."""
        func_list = {}
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                func_list[rule.rule] = (
                    app.view_functions[rule.endpoint].__doc__)
        return json.dumps(func_list)


class Status(Resource):
    def get(self):
        return {
            'connected': printer.isConnected(),
            'locked': True if serial_lock else False}, 201


class Waiting(Resource):
    @connected
    @api_lock
    def get(self):
        return {'size': printer.inWaiting()}, 201


class PortList(Resource):
    def get(self):
        return {'ports': [p for p in printer.list_ports()]}, 201


class History(Resource):
    def get(self):
        """Get history of read, usefull for debugging"""
        return {'data': json.dumps(list(history))}, 201


class DataSend(Resource):
    @connected
    @api_lock
    def post(self):
        logging.debug('send')
        """ Buffer multiple commands"""
        data = StringIO(request.form['data'])
        next_command = request.form.get('response_String')
        for line in data.readlines():
            printer.write(line.encode('ascii'))
            if next_command:
                buffer_length = printer.inWaiting()
                if buffer_length > 0:
                    buffer_read = printer.read(buffer_length)
                    history.append(u'next ' + buffer_read)

        return {'status': 'ok'}, 201

    @connected
    @api_lock
    def put(self):
        """send single command"""
        history.append(u'write %s' % request.form.get('data', ''))
        printer.write(request.form.get('data', '').encode('ascii'))
        return {'status': 'ok'}, 201


class DataRecv(Resource):
    @connected
    @api_lock
    def get(self, length=None):
        buffer_read = ''
        buffer_length = printer.inWaiting()
        if buffer_length > 0:
            if length is None:
                buffer_read = printer.read()
            else:
                buffer_read = printer.recv(buffer_length)
            history.append(u'recv  ' + buffer_read)
        return {'data': buffer_read}, 201


def add_api_endpoints(api_object):
    api_object.add_resource(Connection, '/open')
    api_object.add_resource(History, '/history')
    api_object.add_resource(Status, '/status')
    api_object.add_resource(Waiting, '/waiting')
    api_object.add_resource(PortList, '/ports')
    api_object.add_resource(DataSend, '/write')
    api_object.add_resource(DataRecv, '/recv')
    api_object.add_resource(ClosePort, '/close')


if __name__ == '__main__':
    # add_api_endpoints(api)
    # Actually setup the Api resource routing here
    app.run(host='0.0.0.0', debug=True, port=5005)
