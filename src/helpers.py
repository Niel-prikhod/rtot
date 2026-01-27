import framebuf
import time
from machine import Pin, I2C
from mpu6500 import MPU6500, SF_G, SF_DEG_S
from mpu9250 import MPU9250  # tuupola
from bmp280 import BMP280    # dafvid
from ssd1306 import SSD1306_I2C

def init_i2c():
    # OLED on GP2=SDA, GP3=SCL -> I2C1
    i2c_oled = I2C(1, scl=Pin(3), sda=Pin(2))
    # Sensors on GP4=SDA, GP5=SCL -> I2C0
    i2c_sensors = I2C(0, scl=Pin(5), sda=Pin(4))

    # mpu6500 = MPU6500(i2c_sensors, accel_sf=SF_G, gyro_sf=SF_DEG_S)
    # mpu = MPU9250(i2c_sensors, mpu6500=mpu6500)
    mpu = MPU9250(i2c_sensors)
    bmp = BMP280(i2c_sensors, 0x77)
    oled = SSD1306_I2C(128, 64, i2c_oled)
    return mpu, bmp, oled

def display(oled, *args):
    oled.fill(0)
    for i, text in enumerate(args):
        oled.text(str(text), 0, i*10 + 1, 2)
        oled.show()

def draw_big_number(oled, num, x, y, scale=8):
    text = str(num)
    character_width = 8
    character_height = 8
    width = character_width * len(text)
    height = character_height
    temp_buf = bytearray(width * height // 8)  # Corrected to use bits
    temp_fb = framebuf.FrameBuffer(temp_buf, width, height, framebuf.MONO_VLSB)
    temp_fb.text(text, 0, 0, 1)
    for i in range(width):
        for j in range(height):
            if temp_fb.pixel(i, j):
                oled.fill_rect(x + i * scale, y + j * scale, scale, scale, 1)

def countdown(oled, seconds):
    digit_width = 8 * 8  # scale=8
    digit_height = 8 * 8
    x = (128 - digit_width) // 2
    y = (64 - digit_height) // 2
    
    for i in range(seconds, 0, -1):
        oled.fill(0)
        draw_big_number(oled, i, x, y)
        print(i)
        oled.show()
        time.sleep(1)
    
    oled.fill(0)
    draw_big_number(oled, 0, x, y)
    oled.show()

def apply_calibration(ax, ay, az, gx, gy, gz, mx, my, mz, calib):

    gx -= calib["gyro_bias"]["x"]
    gy -= calib["gyro_bias"]["y"]
    gz -= calib["gyro_bias"]["z"]

    ax = (ax - calib["accel"]["offset"]["x"]) / calib["accel"]["scale"]["x"]
    ay = (ay - calib["accel"]["offset"]["y"]) / calib["accel"]["scale"]["y"]
    az = (az - calib["accel"]["offset"]["z"]) / calib["accel"]["scale"]["z"]

    mx -= calib["mag"]["offset"]["x"]
    my -= calib["mag"]["offset"]["y"]
    mz -= calib["mag"]["offset"]["z"]

    mx *= calib["mag"]["scale"]["x"]
    my *= calib["mag"]["scale"]["y"]
    mz *= calib["mag"]["scale"]["z"]

    return ax, ay, az, gx, gy, gz, mx, my, mz

