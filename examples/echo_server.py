import sys
import logging
from flask import request
from serjax.server import connected, api_lock
from serjax.server import DataSend, DataRecv
from serjax.server import api
from serjax.server import app

logging.basicConfig(level=logging.DEBUG)


class DataSendEcho(DataSend):
    @connected
    @api_lock
    def post(self):
        logging.debug('test post')
        print('Posting = %s' % request.form['data'])
        result = super(DataSendEcho, self).post()
        return result

    @connected
    @api_lock
    def put(self):
        logging.debug('test post')
        sys.stderr.write('test put')
        print('Puting = %s' % request.form['data'], sys.stderr)
        result = super(DataSendEcho, self).put()
        return result


class DataRecvEcho(DataRecv):
    @connected
    @api_lock
    def get(self, length=None):
        logging.debug('test post')
        sys.stderr.write('test get')
        result = super(DataRecvEcho, self).get(length)
        print(result)
        return result


api.add_resource(DataSendEcho, '/write')
api.add_resource(DataRecvEcho, '/recv')

if __name__ == '__main__':
    logging.debug('test post')
    app.run(host='0.0.0.0', debug=True, port=5005)
