SRC_DIR := ports
BIN_DIR := bin

ASM_FILES := $(wildcard $(SRC_DIR)/*.asm)
BIN_FILES := $(patsubst $(SRC_DIR)/%.asm,$(BIN_DIR)/%,$(ASM_FILES))

all: $(BIN_FILES)

$(BIN_DIR)/%: $(SRC_DIR)/%.asm
	@mkdir -p $(BIN_DIR)
	vasm -esc -dotdir -Fbin $< -o $@

clean:
	rm -rf $(BIN_DIR)

flash:
	rm -rf .staging
	mkdir .staging
	rsync -av --exclude='.git' --exclude='__pycache__' ./ .staging/
	- mpremote fs rm -r :/
	mpremote fs cp -r .staging/* :/
	rm -rf .staging

cswap:
	python cswap.py
