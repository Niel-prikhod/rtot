# Paths
MPREMOTE ?= mpremote
PORT ?= /dev/ttyACM0

LIB_DIR := lib
SRC_DIR := src
BUILD_DIR := build

LIBS := ak8963.py  bmp280.py  mpu6500.py  mpu9250.py  ssd1306.py
SRCS := main.py 
MPYS := $(addprefix $(BUILD_DIR)/,$(LIBS:.py=.mpy))

$(BUILD_DIR)/%.mpy: $(LIB_DIR)/%.py | $(BUILD_DIR)
		@mkdir -p $(dir $@)
		mpy-cross $< -o $@

# Ensure build directory exists
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Flash compiled libraries + sources to Pico
flash: mpy
	@echo "Flashing Pico on $(PORT)..."
	$(MPREMOTE) connect $(PORT) rm -r :lib || true
	$(MPREMOTE) connect $(PORT) mkdir :lib
	$(MPREMOTE) connect $(PORT) cp -r $(BUILD_DIR)/* :lib
	# copy all source files
	$(foreach f,$(SRCS),$(MPREMOTE) connect $(PORT) fs cp $(SRC_DIR)/$f :$f;)
	$(MPREMOTE) connect $(PORT) reset
	@echo "Done."

mpy: $(MPYS)

# Run main.py in RAM
run:
	$(MPREMOTE) connect $(PORT) run $(SRC_DIR)/main.py

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)

