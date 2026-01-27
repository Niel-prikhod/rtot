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
	$(MPREMOTE) connect $(PORT) cp data/calibration.json :calibration.json
	# $(MPREMOTE) connect $(PORT) cp -r $(BUILD_DIR)/* :lib
	$(foreach f,$(MPYS),$(MPREMOTE) connect $(PORT) cp $(BUILD_DIR)/$f :lib/$f;)

# Ensure build directory exists
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

sources:
	$(foreach f,$(SRCS),$(MPREMOTE) connect $(PORT) cp $(SRC_DIR)/$f :$f;)

# Flash compiled libraries + sources to Pico
flash: libs sources
	@echo "Flashing Sources on $(PORT)..."
	$(MPREMOTE) connect $(PORT) soft-reset
	@echo "Done."

calibration: libs sources
	$(foreach f,$(CLBS),$(MPREMOTE) connect $(PORT) cp $(CLB_DIR)/$f :$f;)

fetch-data:
	mkdir -p data
	$(eval FILES := $(shell $(MPREMOTE) connect $(PORT) fs ls :data))
	$(foreach f,$(FILES),$(MPREMOTE) connect $(PORT) fs cp :data/$(f) data/;)

run: sources
	$(MPREMOTE) connect $(PORT) run $(SRC_DIR)/main.py

repl:
	$(MPREMOTE) connect $(PORT) repl

# Clean build artifacts
clean:
	@rm -f *.mpy || true 
	@rm -rf $(BUILD_DIR) || true

# Remove all user files from Pico filesystem
pico-clean:
	@echo "Cleaning all files from Pico on $(PORT)..."
	$(MPREMOTE) connect $(PORT) rm -r :lib || true
	$(MPREMOTE) connect $(PORT) rm :*.py || true
	$(MPREMOTE) connect $(PORT) rm :*.mpy || true
	$(MPREMOTE) connect $(PORT) rm -r :data || true
	$(MPREMOTE) connect $(PORT) rm :*.csv || true
	$(MPREMOTE) connect $(PORT) rm :*.json || true
	@echo "Pico filesystem cleaned."

pico-ls: 
	$(MPREMOTE) connect $(PORT) fs ls

re: pico-clean clean flash

