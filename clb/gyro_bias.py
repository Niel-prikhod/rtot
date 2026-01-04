# gyro_bias.py
from calib_logger import record_to_csv
from mpu9250 import MPU9250 as mpu

def read_gyro_sample():
    gx, gy, gz = mpu.gyro  # adapt to your driver API; expected deg/s
    return (gx, gy, gz)

# collect 2000 samples at 100Hz (20s)
record_to_csv('/calib/gyro_bias.csv', ['t','gx','gy','gz'], read_gyro_sample, sample_rate_hz=100, max_seconds=20)

