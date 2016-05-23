import glob
import serial
import logging

""" 
    usefull for testing, setup fake serial ports and monitor in screen
    #socat -d -d pty,raw,echo=0 pty,raw,echo=0
    #screen /dev/ttyUSB0 57600
"""

class serialPort():
    port = '/dev/ttyACM0'
    coms = None
    connected = False

    def isConnected(self):
        return self.connected

    def connect(self, port='/tmp/ttyS11'):
        self.port = port
        try:
            self.coms = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=0,
                rtscts=True, dsrdtr=True
            )
            
            self.connected = self.coms.isOpen()
            return self.connected
        except Exception as e:
            logging.error(e)
            self.connected = False
            return False

    def list_ports(self):
        for port in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
            yield port


    def inWaiting(self):
        return self.coms.inWaiting()

    def write(self, data):
        self.coms.write(data)

    def send(self, data):
        self.coms.write(data)

    def recv(self):
        out = ''
        while self.coms.inWaiting() > 0:
            out += self.coms.read(1)
        return out

    def receive(self):
        out = ''
        while self.coms.inWaiting() > 0:
            out += self.coms.read(1)
        return out

    def close(self):
        if self.connected is True:
            self.coms.close()
