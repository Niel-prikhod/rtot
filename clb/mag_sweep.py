# mag_sweep.py
from calib_logger import record_to_csv
# from your_mpu_module import mpu  # needs mpu.mag or similar

def read_mag_sample():
    mx, my, mz = mpu.mag  # uT or driver units
    return (mx, my, mz)

# record for 60 seconds at 50Hz
record_to_csv('/calib/mag_sweep.csv', ['t','mx','my','mz'], read_mag_sample, sample_rate_hz=50, max_seconds=60)

