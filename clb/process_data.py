import numpy as np
import json
from pathlib import Path

# Set up proper paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "../data"


### accel data read


def axis_calib(pos_file, neg_file, axis):
    p = np.loadtxt(pos_file, delimiter=",", skiprows=1)[:, axis].mean()
    n = np.loadtxt(neg_file, delimiter=",", skiprows=1)[:, axis].mean()
    offset = (p + n) / 2
    scale = (p - n) / 2
    return offset, scale

accel_calib = {}
accel_calib["x"] = axis_calib(str(DATA_DIR / "accel_right-x.csv"), str(DATA_DIR / "accel_left+x.csv"), 1)
accel_calib["y"] = axis_calib(str(DATA_DIR / "accel_tail-y.csv"), str(DATA_DIR / "accel_nose+y.csv"), 2)
accel_calib["z"] = axis_calib(str(DATA_DIR / "accel_flat-z.csv"), str(DATA_DIR / "accel_flat+z.csv"), 3)

accel_offset = {
    "x": accel_calib["x"][0],
    "y": accel_calib["y"][0],
    "z": accel_calib["z"][0]
}
accel_scale = {
    "x": accel_calib["x"][1],
    "y": accel_calib["y"][1],
    "z": accel_calib["z"][1]
}


### gyro data read


data = np.loadtxt(str(DATA_DIR / "gyro_bias.csv"), delimiter=",", skiprows=1)
gx, gy, gz = data[:,1], data[:,2], data[:,3]

gyro_bias = {
    "x": gx.mean(),
    "y": gy.mean(),
    "z": gz.mean()
}


### magn data read 


data = np.loadtxt(str(DATA_DIR / "mag_sweep.csv"), delimiter=",", skiprows=1)
mx, my, mz = data[:,1], data[:,2], data[:,3]

hard_iron = {
    "x": (mx.max() + mx.min()) / 2,
    "y": (my.max() + my.min()) / 2,
    "z": (mz.max() + mz.min()) / 2
}

mx_c = mx - hard_iron["x"]
my_c = my - hard_iron["y"]
mz_c = mz - hard_iron["z"]

# simple diagonal soft-iron scaling
sx = (mx_c.max() - mx_c.min()) / 2
sy = (my_c.max() - my_c.min()) / 2
sz = (mz_c.max() - mz_c.min()) / 2

avg_scale = (sx + sy + sz) / 3

mag_scale = {
    "x": avg_scale / sx,
    "y": avg_scale / sy,
    "z": avg_scale / sz
}


### data rearrangement


calibration = {
    "gyro_bias": {
        "x": float(gyro_bias["x"]),
        "y": float(gyro_bias["y"]),
        "z": float(gyro_bias["z"])
    },
    "accel": {
        "offset": {
            "x": float(accel_offset["x"]),
            "y": float(accel_offset["y"]),
            "z": float(accel_offset["z"])
        },
        "scale": {
            "x": float(accel_scale["x"]),
            "y": float(accel_scale["y"]),
            "z": float(accel_scale["z"])
        }
    },
    "mag": {
        "offset": {
            "x": float(hard_iron["x"]),
            "y": float(hard_iron["y"]),
            "z": float(hard_iron["z"])
        },
        "scale": {
            "x": float(mag_scale["x"]),
            "y": float(mag_scale["y"]),
            "z": float(mag_scale["z"])
        }
    }
}


# json fill
with open(str(DATA_DIR / "calibration.json"), "w") as f:
    json.dump(calibration, f, indent=2)

print("Calibration written to calibration.json")

