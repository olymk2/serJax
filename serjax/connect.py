import glob
import serial
import logging


class serialPort():
    """ Serial port wrapper """
    port = '/dev/ttyACM0'
    coms = None
    connected = False

    def isOpen(self):
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
            return '' #self.connected
        except Exception as e:
            logging.error(e)
            self.connected = False
            return str(e)

    def list_ports(self, pty=True):
        for port in glob.glob('/dev/ttyUSB*'):
            yield port
        for port in glob.glob('/dev/ttyACM*'):
            yield port
        if pty is False:
            return

        for port in glob.glob('/dev/pts/*'):
            yield port
        for port in glob.glob('/dev/ptmx'):
            yield port

    def inWaiting(self):
        return self.coms.inWaiting()

    def write(self, data):
        self.coms.write(data)

    def send(self, data):
        self.coms.write(data)

    def read(self):
        """ Read entire buffer """
        out = ''
        while self.coms.inWaiting():
            out += self.coms.read(1)
        return out

    def recv(self, length=1):
        """ Read limited length buffer"""
        out = ''
        if self.coms.inWaiting() >= length:
            out = self.coms.read(1)
        return out

    def receive(self):
        out = ''
        while self.coms.inWaiting() > 0:
            out += self.coms.read(1)
        return out

    def close(self):
        if self.connected is True:
            self.coms.close()
