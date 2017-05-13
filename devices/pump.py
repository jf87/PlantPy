import machine


class Pump:
    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.OUT)
        self.pin.low()
        self.state = 0

    def on(self):
        self.pin.high()
        self.state = 1

    def off(self):
        self.pin.low()
        self.state = 0
