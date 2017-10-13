from machine import UART
from machine import Pin
import os
from network import WLAN
import config as C


uart = UART(0, 115200)
os.dupterm(uart)
pin = Pin("P19", Pin.OUT)
pin.value(0)

wlan = WLAN(mode=WLAN.STA)
wlan.scan()

wlan.connect(ssid=C.SSID, auth=(WLAN.WPA2, C.KEY))

while not wlan.isconnected():
    pass

print(wlan.ifconfig())
