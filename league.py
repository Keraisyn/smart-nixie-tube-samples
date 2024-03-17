from machine import Pin, Timer
import network
import time
import urequests

WIFI_SSID = "<ssid>"
WIFI_PASSWORD = "<password>"
SERVER_URL = "<server url>"


PIN_LIST = [
    # A   B   C   D  (GPIO pin numbers)
    [28, 26, 22, 27],   # 1's
    [20, 18, 17, 19],   # 10's
    [15, 13, 12, 14],   # 100's
    [10,  8,  7,  9],   # 1000's
]


def pin_list_to_pins(pin_list):
    for i in range(len(pin_list)):
        for j in range(len(pin_list[i])):
            pin_list[i][j] = Pin(pin_list[i][j], Pin.OUT)


# Sets the given pins to the 1's digit of value.
# pins - [A, B, C, D]
# value - 0 to 9
def set_digit(pins, value):
    pins[0].value(value % 2)
    value //= 2
    pins[1].value(value % 2)
    value //= 2
    pins[2].value(value % 2)
    value //= 2
    pins[3].value(value % 2)


# Sets the given pins to len(pins_list) digits of value.
# pins - [ [A, B, C, D], ... ]
# value - integer
def set_number(pins_list, value):
    for digit in pins_list:
        set_digit(digit, value % 10)
        value //= 10


if __name__ == "__main__":
    
    # INITIALIZE PINS
    pin_list_to_pins(PIN_LIST)
    for digit in PIN_LIST:
        for pin in digit:
            pin.value(0)


    ##### WIFI START ##########
    ssid = WIFI_SSID
    password = WIFI_PASSWORD
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("[Info] Connecting...")
        time.sleep(1)

    # Handle errors
    if wlan.status() != 3:
        print("[Error] Network connection failed.")
        set_number(PIN_LIST, 1111)
    else:
        print("[Info] Connected.")
        status = wlan.ifconfig()
        print( "[Info] ip = " + status[0])

    ##### WIFI END ##########


    def web_server_request_callback(t):
        print("[Info] Making request")
        r = urequests.get(
            "{}/api/leaguelastplayed"
            .format(SERVER_URL)
        )
        if r.status_code != 200:
            print("[Error] Server did not return valid reponse.")
            return
        
        n = 0
        
        try:
            n = int(r.json()['number'])
            print("[Info] Got number", n)
        except:
            pass

        if (n >= 10000):
            n = 9999
        elif (n < 0):
            n = 0

        set_number(PIN_LIST, n)

    # Run once every minute
    web_server_request_callback(None)
    timer = Timer()
    timer.init(
        period=60000, 
        mode=Timer.PERIODIC, 
        callback=web_server_request_callback
    )
