import machine


class Pump:
    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.OUT)
        self.pin.value(0)
        self.state = 0

    def on(self):
        self.pin.value(1)
        self.state = 1

    def off(self):
        self.pin.value(0)
        self.state = 0
