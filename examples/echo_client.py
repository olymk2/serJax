# Example program connecting to the server and printing
# this just dumps the responses to the command line
import os
import pty
from serjax.client import serial

master_pty, slave_pty = pty.openpty()
slave_port = os.ttyname(slave_pty)
master_port = os.ttyname(master_pty)

with serial(url='http://localhost:5005') as client:
    print('List ports')
    print("\t%s" % client.ports())
    print('Open port')
    print("\t%s" % client.open(slave_port))
    print('Client isConnected')
    print("\t%d" % client.isConnected())
    print('Client status')
    print("\t%s" % client.status())

    # you should see this pop up in the echo server logs 
    client.write('test first message')


    print('Read text on serial buffer')
    os.write(master_pty, 'Read text on serial buffer')
    print("\t%s" % client.read())

    os.write(master_pty, 'test second message')
    print("\t%s" % client.read())
