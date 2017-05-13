import time
from machine import I2C
from struct import unpack


class Chirp:
    def __init__(self, address):
        self.i2c = I2C(0, I2C.MASTER, baudrate=10000)
        self.address = address

    def get_reg(self, reg):
        val = unpack('<H', (self.i2c.readfrom_mem(self.address, reg, 2)))[0]
        return (val >> 8) + ((val & 0xFF) << 8)

    def moist(self):
        return self.get_reg(0)

    def temp(self):
        return self.get_reg(5)

    def light(self):
        self.i2c.writeto(self.address, '\x03')
        time.sleep(1.5)
        return self.get_reg(4)
