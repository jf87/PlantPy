from machine import UART
import os
from network import WLAN
import config as C


uart = UART(0, 115200)
os.dupterm(uart)

wlan = WLAN(mode=WLAN.STA)
wlan.scan()

wlan.connect(ssid=C.SSID, auth=(WLAN.WPA2, C.KEY))

while not wlan.isconnected():
    pass

print(wlan.ifconfig())
