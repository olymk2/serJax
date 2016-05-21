#!/usr/bin/python
# -*- coding: utf-8 -*-
__version__ = '0.1.1'

import os
import sys
import urllib
import random
from io import StringIO

sys.path.append(os.path.abspath('../../../'))

from connect import serialPort

from flask import Flask
from flask import request
from flask_restful import reqparse, abort, Api, Resource

serial_lock = None
printer = serialPort()
root_url = 'http://127.0.0.1:5005/'

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

def api_lock(func):
    """decorator to check the api is not locked and 404 if it is locked or not locked by current user"""
    def func_wrapper(name):
        request_lock = request.headers.get('api_lock')

        if request_lock is None:
            return abort(404, message='You do not have a lock on this resource')

        if str(serial_lock) == str(request_lock):
            return func(name)

        return abort(404, message='Api locked by another user')
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
        serial_lock = random.getrandbits(128)
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
                func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
        return jsonify(func_list)

class PortList(Resource):
    def get(self):
        portlist = {}
        for p in printer.list_ports():
            portlist[p] = '%sconnect/%s' % (root_url, urllib.quote(p.strip('/')))
        return portlist, 201

class DataSend(Resource):
    @connected
    @api_lock
    def post(self):
        """ Buffer multiple commands"""
        data = StringIO(request.form['data'])
        for line in data.readlines():
            printer.write(bytes(line))
        return {'status': 'ok'}, 201

    @connected
    @api_lock
    def put(self):
        """send single command"""
        printer.write(bytes(request.form.get('data', '')))
        return {'status': 'ok'}, 201

class DataRecv(Resource):
    @connected
    @api_lock
    def get(self):
        return {'data': 'Ok'}, 201

## Actually setup the Api resource routing here

api.add_resource(Connection, '/open')
api.add_resource(PortList, '/ports')
api.add_resource(DataSend, '/write')
api.add_resource(DataRecv, '/recv')
api.add_resource(ClosePort, '/close')

if __name__ == '__main__':
    app.run(debug=True, port=5005)

#serJax
