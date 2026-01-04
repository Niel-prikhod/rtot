from machine import I2C, Pin
import ssd1306
import bmp280
from mpu9250 import MPU9250

# OLED on GP2=SDA, GP3=SCL -> I2C1
i2c_oled = I2C(1, scl=Pin(3), sda=Pin(2))

# Sensors on GP4=SDA, GP5=SCL -> I2C0
i2c_sensors = I2C(0, scl=Pin(5), sda=Pin(4))

# Initialize devices
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)
bmp = bmp280.BMP280(i2c_sensors, 0x77)
imu = MPU9250(i2c_sensors)

oled.text("Hello Pico!", 0, 0)
oled.show()

while(True):
    print([hex(x) for x in i2c_sensors.scan()])
    print("BMP280 Temp:", bmp.temperature)
    print("IMU Accel:", imu.acceleration)
