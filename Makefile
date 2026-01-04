# Paths
MPREMOTE ?= mpremote
PORT ?= /dev/ttyACM0

LIB_DIR := lib
SRC_DIR := src
CLB_DIR := clb
BUILD_DIR := build

LIBS := ak8963.py  bmp280.py  mpu6500.py  mpu9250.py  ssd1306.py
SRCS := main.py helpers.py
CLBS:= calibrate.py calib_logger.py

MPYS := $(LIBS:.py=.mpy)

$(BUILD_DIR)/%.mpy: $(LIB_DIR)/%.py | $(BUILD_DIR)
		@mkdir -p $(dir $@)
		mpy-cross $< -o $@

mpy: $(addprefix $(BUILD_DIR)/,$(MPYS))

libs: mpy
	$(MPREMOTE) connect $(PORT) rm -r :lib || true
	$(MPREMOTE) connect $(PORT) mkdir :lib
	@echo "Flashing Libraries on $(PORT)..."
	# $(MPREMOTE) connect $(PORT) cp -r $(BUILD_DIR)/* :lib
	$(foreach f,$(MPYS),$(MPREMOTE) connect $(PORT) cp $(BUILD_DIR)/$f :$f;)

# Ensure build directory exists
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Flash compiled libraries + sources to Pico
flash: libs
	@echo "Flashing Sources on $(PORT)..."
	# copy all source files
	$(foreach f,$(SRCS),$(MPREMOTE) connect $(PORT) cp $(SRC_DIR)/$f :$f;)
	$(MPREMOTE) connect $(PORT) reset
	@echo "Done."

calibrate: libs
	$(foreach f,$(SRCS),$(MPREMOTE) connect $(PORT) cp $(SRC_DIR)/$f :$f;)
	$(foreach f,$(CLBS),$(MPREMOTE) connect $(PORT) cp $(CLB_DIR)/$f :$f;)
	$(MPREMOTE) connect $(PORT) run calibrate.py

fetch-data:
	mkdir -p data
	$(MPREMOTE) connect $(PORT) fs cp :data/*.csv data/
	$(MPREMOTE) connect $(PORT) fs cp :data/*.json data/

# Run main.py in RAM
run:
	$(MPREMOTE) connect $(PORT) run $(SRC_DIR)/main.py

repl:
	$(MPREMOTE) connect $(PORT) repl

# Clean build artifacts
clean:
	rm *.mpy || true 
	rm -rf $(BUILD_DIR) || true

# Remove all user files from Pico filesystem
pico-clean:
	@echo "Cleaning all files from Pico on $(PORT)..."
	$(MPREMOTE) connect $(PORT) fs rm -r :lib || true
	$(MPREMOTE) connect $(PORT) fs rm :*.py || true
	$(MPREMOTE) connect $(PORT) fs rm :*.mpy || true
	$(MPREMOTE) connect $(PORT) fs rm -r :data || true
	$(MPREMOTE) connect $(PORT) fs rm :*.csv || true
	$(MPREMOTE) connect $(PORT) fs rm :*.json || true
	@echo "Pico filesystem cleaned."

re: pico-clean clean flash

