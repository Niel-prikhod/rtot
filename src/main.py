import time
import helpers
import math

P_0 = 101325
ALPHA_P = 0.3
TARGET_HZ = 5
DT = 1.0 / TARGET_HZ

def main(): 
    mpu, bmp, oled = helpers.init_i2c()
    
    helpers.countdown(oled, 5)
    last = time.ticks_us()

    p_smoothed = None

    while True:
        now = time.ticks_us()
        dt = (time.ticks_diff(now, last)) / 1_000_000  # seconds
        if dt < DT:
            time.sleep_us(int((DT - dt) * 1_000_000))
            continue
        last = time.ticks_us()
        
        ax, ay, az = mpu.acceleration
        gx, gy, gz = mpu.gyro 
        mx, my, mz = mpu.magnetic 
        temp = bmp.temperature
        pressure = bmp.pressure
        
        roll  = math.atan2(ay, az)
        pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))
        
        mx2 = mx * math.cos(pitch) + mz * math.sin(pitch)
        my2 = mx * math.sin(roll) * math.sin(pitch) + my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)
        yaw = math.atan2(-my2, mx2)

        roll_deg  = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg   = math.degrees(yaw)

        if p_smoothed is None:
            p_smoothed = pressure
        p_smoothed = ALPHA_P * p_smoothed + (1 - ALPHA_P) * pressure
        
        h = 44330.0 * (1.0 - pow(p_smoothed / P_0, 1.0 / 5.255))

        h_text = "altitude = " + str(h)
        roll_text = "roll = " + str(roll_deg)  
        pitch_text = "pitch = " + str(pitch_deg)
        yaw_text = "yaw = " + str(yaw_deg)  

        helpers.display(oled, temp, h_text, roll_text, pitch_text, yaw_text)

if __name__ == "__main__":
    main()
