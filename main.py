import ujson
from utime import sleep
import gc
import flickapi
from definitions import CONFIG_PATH
#import wifimanager
import captive_portal

gc.enable()

print("booted")

#wlan_sta = network.WLAN(network.STA_IF)
#if not wlan_sta.isconnected():
#    print("wifimgr")
#    wlan = wifimgr.get_connection()
#    if not wlan:
#        print("Could not initialize the network connection.")
#        while True:
#            pass  # you shall not pass :D
#wlan_sta = None

#wifi = wifimanager.WiFiManager()
#if wifi.get_connection() is None:
#    print("failed to connect")
#    while True:
#        pass  # you shall not pass :D
#else:
#    print("not connected")
#wifi = None

portal = captive_portal.CaptivePortal("Testing")
print("starting captive portal")
portal.captive_portal()

print("MicroFlick starting up")

with open(CONFIG_PATH) as fp:
    config_data = ujson.load(fp)

flick = flickapi.Flick(config_data["client_id"],
                       config_data["client_secret"],
                       config_data["username"],
                       config_data["password"])
while True:
    if flick.authenticate():
        print(flick.get_price_per_kwh())
    else:
        print("skipping get_price")
    sleep(60)
