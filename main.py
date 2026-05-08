import machine
import time
import math

SEGMENTS = [machine.Pin(i, machine.Pin.OUT) for i in range(8)]
DIGITS = [machine.Pin(i, machine.Pin.OUT) for i in range(11, 7, -1)]

btn = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
analog_in = machine.ADC(machine.Pin(26))

display_value = 0.0
last_button_press = 0
current_digit = 0
display_timer = machine.Timer(-1)

NUMBERS = [
    [0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 1],
    [0, 0, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 1, 0],
    [1, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0]
]

def read_analogue_voltage(pin):
    global display_value, last_button_press
    current_time = time.ticks_ms()
    
    if time.ticks_diff(current_time, last_button_press) > 200:
        last_button_press = current_time
        
        sum_val = 0
        for _ in range(16):
            sum_val += analog_in.read_u16()
        avg_val = sum_val / 16
        
        display_value = (avg_val / 65535.0) * 3.3
        print(f"Voltage: {display_value:.3f} V")
        
        try:
            BETA = 3950
            if 0 < avg_val < 65535:
                celsius = 1 / (math.log(1 / (65535.0 / avg_val - 1)) / BETA + 1.0 / 298.15) - 273.15
                print(f"Calculated Temperature: {celsius:.1f} C")
        except Exception:
            pass

def scan_display(timer):
    global current_digit, display_value
    
    val_str = f"{display_value:05.3f}".replace(".", "")
    if len(val_str) > 4: 
        val_str = val_str[:4]
    
    for d in DIGITS:
        d.value(0)
    
    num = int(val_str[current_digit])
    for i in range(7):
        SEGMENTS[i].value(NUMBERS[num][i])
        
    if current_digit == 0:
        SEGMENTS[7].value(0)
    else:
        SEGMENTS[7].value(1)
        
    DIGITS[current_digit].value(1)
    
    current_digit = (current_digit + 1) % 4

def enable_display_timer():
    display_timer.init(period=5, mode=machine.Timer.PERIODIC, callback=scan_display)

def setup():
    btn.irq(trigger=machine.Pin.IRQ_FALLING, handler=read_analogue_voltage)

if __name__ == '__main__':
    setup()
    enable_display_timer()
    
    while True:
        time.sleep(0.1)