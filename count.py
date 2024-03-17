from machine import Pin, Timer

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
    
    pin_list_to_pins(PIN_LIST)

    for digit in PIN_LIST:
        for pin in digit:
            pin.value(0)

    timer = Timer()

    count = 0

    def countup_callback(t):
        global count
        set_number(PIN_LIST, count)
        if count >= 9999:
            count = 0
        else:
            count += 1

    timer.init(freq=10, mode=Timer.PERIODIC, callback=countup_callback)
