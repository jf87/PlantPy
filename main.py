import pycom
import machine
import time
from network import LoRa
from network import Bluetooth
from dev.chirp import Chirp
from dev.pump import Pump
import config as C
import requests as R
import utime
import ujson
import os


def setup_leds():
    if C.HEARTBEAT_LED_ENABLED:
        pass
    else:
        pycom.heartbeat(False)


def setup_ble():
    bt = Bluetooth()
    if C.BLE_ENABLED:
        bt.set_advertisement(name="LoPy")
        bt.advertise(True)
    else:
        bt.deinit()


def setup_lora():
    lora = LoRa()
    if C.LORAWAN_ENABLED:
        pass
    else:
        lora.init(power_mode=LoRa.SLEEP)


def setup_time(diff):
    rtc = machine.RTC()
    rtc.ntp_sync("pool.ntp.org")
    utime.sleep_ms(2000)
    print('\nRTC Set from NTP to UTC:', rtc.now())
    utime.timezone(diff)
    print('Adjusted from UTC to local timezone', utime.localtime(), '\n')


def setup_meta(directory):
    meta = []
    print(os.listdir())
    for n in os.listdir(directory):
        print(n)
        f = open(directory+"/"+n)
        m = f.read()
        f.close()
        meta.append(ujson.loads(m))
    return meta


def post_data(meta):
    for m in meta:
        if len(m["Readings"]) > 0:
            s = {m["Path"]: m}
            body = ujson.dumps(s)
            r = R.Requests("POST", C.URL, data=body, headers=C.HEADERS)
            try:
                r.makeRequest()
            except:
                pass
            # print(r.status_code)
            # if (r.status_code) == 200:
            m["Readings"] = []
            # else:
            #     print("POST not successful")
    return meta


def post_data_fake(meta):
    for m in meta:
        print("post")
        print(m)
        if len(m["Readings"]) > 0:
            s = {m["Path"]: m}
            body = ujson.dumps(s)
            if  True:
                m["Readings"] = []
            else:
                print("POST not successful")
    return meta


def actuate(meta, pump):
    actuated = False
    t_on = 0
    s_on = 0
    t_off = 0
    s_off = 0
    for m in meta:
        if m["Metadata"]["Extra"]["Type"] == "Moisture":
            print(m)
            l = len(m["Readings"])
            print(l)
            if l > 0:
                s = 0
                for r in m["Readings"]:
                    s = s + r[1]
                avg = s/l
                print(avg)
                # FIXME is this a good value? does it change over time?
                if avg < 400:
                    t_on = int(utime.time())*1000
                    pump.on()
                    s_on = pump.state
                    time.sleep_ms(1000)
                    pump.off()
                    s_off = pump.state
                    t_off = int(utime.time())*1000
                    actuated = True
    if actuated:  # FIXME not very nice
        for m in meta:
            if m["Metadata"]["Extra"]["Type"] == "Pump":
                m["Readings"].append([t_on, s_on])
                m["Readings"].append([t_off, s_off])
    return meta


if __name__ == "__main__":
    p = Pump(C.PUMP_PIN)
    setup_leds()
    setup_ble()
    setup_lora()
    time.sleep(2)
    setup_time(3600)  # from UTC to CET
    meta = setup_meta("./meta")  # one time metasetup
    c = Chirp(C.CHIRP_ADDRESS)
    while True:
        for i in range(0, C.POST_INTERVAL):
            for m in meta:
                t = int(utime.time())*1000
                if (m["Metadata"]["Extra"]["Type"] == "Temperature"):
                    v = c.temp()/10
                elif (m["Metadata"]["Extra"]["Type"] == "Moisture"):
                    v = c.moist()
                elif (m["Metadata"]["Extra"]["Type"] == "Light"):
                    v = c.light()
                    v = 100 * ((65535 - v) / 65535)
                elif (m["Metadata"]["Extra"]["Type"] == "Pump"):
                    v = p.state
                m["Readings"].append([t, v])
            time.sleep(C.SAMPLING_INTERVAL)
        meta = actuate(meta, p)
        meta = post_data(meta)
