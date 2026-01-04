# accel_sixpos.py
import time
from machine import Pin
from calib_logger import record_to_csv, timestamp
from mpu9250 import MPU9250 as mpu

POSITIONS = ['flat+z', 'flat-z', 'left+x', 'right-x', 'nose+y', 'tail-y']

def read_accel_sample():
    ax, ay, az = mpu.accel  # adapt units (g)
    return (ax, ay, az)

for pos in POSITIONS:
    print("Place device:", pos)
    print("Starting capture in 2s...")
    time.sleep(2)
    filename = '/calib/accel_{}.csv'.format(pos)
    record_to_csv(filename, ['t','ax','ay','az'], read_accel_sample, sample_rate_hz=100, max_seconds=3)
    print("Saved", filename)
    # wait for button release to move on
    time.sleep(0.3)

