# calibrate.py
"""
Run a full calibration sequence on the Pico:
  1) Gyro bias (stationary)
  2) Accelerometer six-position (one file per position)
  3) Magnetometer sweep (rotate slowly during capture)
"""

import ujson
import time

from calib_logger import record_to_csv, ensure_dir, timestamp
import helpers 

# --- Configuration (tweak as needed) ---
BASE_DIR = "/data"
POSITIONS = ['flat+z', 'flat-z', 'left+x', 'right-x', 'nose+y', 'tail-y']

# sampling defaults
GYRO_RATE_HZ = 100
GYRO_SECONDS = 20

ACCEL_RATE_HZ = 100
ACCEL_SECONDS = 3

MAG_RATE_HZ = 50
MAG_SECONDS = 60
# --------------------------------------


def main():
    ensure_dir(BASE_DIR)
    mpu, bmp, oled = helpers.init_i2c()

    manifest = {
        "sequence_started_at": timestamp(),
        "stages": []
    }

    def _run_stage(name, filename, fieldnames, read_fn, sample_rate_hz, duration_s):
        stage = {
            "name": name,
            "filename": filename,
            "fieldnames": fieldnames,
            "sample_rate_hz": sample_rate_hz,
            "duration_s": duration_s,
            "started_at": None,
            "finished_at": None,
            "status": "pending"
        }
        try:
            helpers.countdown(oled, 5)

            stage['started_at'] = timestamp()
            record_to_csv(filename, fieldnames, read_fn, sample_rate_hz=sample_rate_hz, max_seconds=duration_s)
            stage['finished_at'] = timestamp()
            stage['status'] = "ok"
            print("Stage", name, " done:")
        except Exception as e:
            stage['finished_at'] = timestamp()
            stage['status'] = "error"
            stage['error'] = str(e)
            print("Stage", name, "failed:", e)
        manifest['stages'].append(stage)
        return stage

    # --- Stage 1: Gyro bias ---
    def read_gyro_sample():
        gx, gy, gz = mpu.gyro
        return (gx, gy, gz)

    gyro_file = "{}/gyro_bias.csv".format(BASE_DIR)
    _run_stage(
        name="gyro_bias",
        filename=gyro_file,
        fieldnames=['t', 'gx', 'gy', 'gz'],
        read_fn=read_gyro_sample,
        sample_rate_hz=GYRO_RATE_HZ,
        duration_s=GYRO_SECONDS
    )

    # small pause between stages
    time.sleep(5.2)

    # --- Stage 2: Accelerometer six-position captures ---
    def read_accel_sample():
        ax, ay, az = mpu.acceleration
        return (ax, ay, az)

    for pos in POSITIONS:
        print("Prepare position:", pos)
        helpers.countdown(oled, 5)
        accel_file = "{}/accel_{}.csv".format(BASE_DIR, pos)
        # call _run_stage which will call helpers.countdown(oled, 5) before capturing
        _run_stage(
            name="accel_" + pos,
            filename=accel_file,
            fieldnames=['t', 'ax', 'ay', 'az'],
            read_fn=read_accel_sample,
            sample_rate_hz=ACCEL_RATE_HZ,
            duration_s=ACCEL_SECONDS
        )
        time.sleep(0.2)

    # --- Stage 3: Magnetometer sweep ---
    def read_mag_sample():
        mx, my, mz = mpu.magnetic
        return (mx, my, mz)

    mag_file = "{}/mag_sweep.csv".format(BASE_DIR)
    print("Start magnetometer sweep: rotate the board slowly for the duration.")
    _run_stage(
        name="mag_sweep",
        filename=mag_file,
        fieldnames=['t', 'mx', 'my', 'mz'],
        read_fn=read_mag_sample,
        sample_rate_hz=MAG_RATE_HZ,
        duration_s=MAG_SECONDS
    )

    manifest['sequence_finished_at'] = timestamp()

    # Save manifest to disk
    try:
        with open("{}/manifest.json".format(BASE_DIR), "w") as mf:
            ujson.dump(manifest, mf)
    except Exception as e:
        manifest['manifest_save_error'] = str(e)
        print("Failed to save manifest:", e)

    # final status print
    print("Calibration sequence complete. Manifest:")
    print(ujson.dumps(manifest, indent=2))

    return manifest


if __name__ == "__main__":
    main()

