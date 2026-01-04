import time
import helpers

def main(): 
    mpu, bmp, oled = helpers.init_i2c()
    # fixed timestep loop variables
    TARGET_HZ = 20
    DT = 1.0 / TARGET_HZ

    last = time.ticks_us()
    while True:
        now = time.ticks_us()
        dt = (time.ticks_diff(now, last)) / 1_000_000  # seconds
        if dt < DT:
            time.sleep_us(int((DT - dt) * 1_000_000))
            continue
        last = time.ticks_us()
        
        helpers.countdown(oled, 5)
        ax, ay, az = mpu.acceleration
        gx, gy, gz = mpu.gyro 
        mx, my, mz = mpu.magnetic 
        temp = bmp.temperature
        pressure = bmp.pressure

        # feed to your filter and update oled
        # roll, pitch, yaw = filter.update(ax, ay, az, gx, gy, gz, mx, my, mz, dt)
        # display(roll, pitch, yaw, temp, pressure)
        helpers.display(oled, temp, pressure, ax, ay, az)

if __name__ == "__main__":
    main()
