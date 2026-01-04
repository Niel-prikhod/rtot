from machine import I2C, Pin
i2c = I2C(0, sda=Pin(4), scl=Pin(5))   # use your sensor bus
addr = 0x68

def peek(reg):
    try:
        b = i2c.readfrom_mem(addr, reg, 1)
        val = int.from_bytes(b, "little")
        print("reg 0x%02x -> 0x%02x" % (reg, val))
        return val
    except Exception as e:
        print("read error:", e)
        return None

print("I2C scan:", [hex(x) for x in i2c.scan()])
peek(0x00)        # WHO_AM_I (ICM20948 typically returns 0xEA)
peek(0x7F)        # REG_BANK_SEL (read current bank)

# write bank 0 then read WHO_AM_I
i2c.writeto_mem(addr, 0x7F, bytes([0x00]))   # select bank 0
peek(0x00)

