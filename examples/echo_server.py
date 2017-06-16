# Wrap data send and receive with log messages to show whats happening
import logging
from flask import request
from serjax.server import connected, api_lock
from serjax.server import DataSend, DataRecv
from serjax.server import api
from serjax.server import app, add_api_endpoints

logging.basicConfig(level=logging.DEBUG)


class DataSendEcho(DataSend):
    @connected
    @api_lock
    def post(self):
        logging.info('Posting = %s' % request.form['data'])
        result = super(DataSendEcho, self).post()
        logging.info(result)
        return result

    @connected
    @api_lock
    def put(self):
        logging.info('Puting = %s' % request.form['data'])
        result = super(DataSendEcho, self).put()
        logging.info(result)
        return result


# class DataRecvEcho(DataRecv):
#     @connected
#     @api_lock
#     def get(self, length=None):
#         logging.info('Data being received')
#         result = super(DataRecvEcho, self).get(length)
#         logging.info(result)
#         return result


# register these first, this stops them being registered in add_api_endpoints
api.add_resource(DataSendEcho, '/write')
# api.add_resource(DataRecvEcho, '/recv')
add_api_endpoints(api)


if __name__ == '__main__':
    logging.debug('test post')
    app.run(host='0.0.0.0', debug=True, port=5005)
