# calib_logger.py
import time
import ujson
from machine import Pin
from os import mkdir

# configure these to your drivers / pins
BTN_PIN = 14        # push button to start/stop
LED_PIN = 25        # onboard LED on many Pico's; else use other gp
SENSOR_I2C = None   # import/instantiate your sensor object in main script

btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT)

def ensure_dir(path):
    try:
        mkdir(path)
    except OSError:
        pass

def timestamp():
    # seconds since boot with subsecond resolution
    return time.ticks_ms() / 1000.0

def record_to_csv(filename, fieldnames, read_sample_fn, sample_rate_hz=50, max_seconds=60*5):
    """
    - filename: '/calib/gyro_bias.csv' etc
    - fieldnames: list of column names
    - read_sample_fn: function returning list/tuple of values matching fieldnames
    - sample_rate_hz: sampling frequency
    """
    ensure_dir('/calib')
    dt = 1.0 / sample_rate_hz
    with open(filename, 'w') as f:
        f.write(','.join(fieldnames) + '\n')
        end_time = timestamp() + max_seconds
        while timestamp() < end_time:
            t = timestamp()
            vals = read_sample_fn()
            line = "{:.6f},".format(t) + ','.join("{:.6f}".format(v) for v in vals) + '\n'
            f.write(line)
            # LED blink to show activity
            led.value(1)
            time.sleep_ms(5)
            led.value(0)
            # sleep remaining time
            elapsed = timestamp() - t
            if elapsed < dt:
                time.sleep(dt - elapsed)

