import os
import pty
from serjax.client import serial

master_pty, slave_pty = pty.openpty()
slave_port = os.ttyname(slave_pty)
master_port = os.ttyname(master_pty)

with serial(url='http://localhost:5005') as client:
    # client.open(slave_port)
    print(client.status())
    client.write('testing')
