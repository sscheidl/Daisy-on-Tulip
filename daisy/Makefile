MIDI_BACKEND ?= DIN
VALID_BACKENDS = DIN USB_INTERNAL USB_EXTERNAL
ifeq ($(filter $(MIDI_BACKEND),$(VALID_BACKENDS)),)
$(error MIDI_BACKEND must be one of $(VALID_BACKENDS))
endif
TARGET = daisy_toy_piano_$(MIDI_BACKEND)
CPP_SOURCES = src/main.cpp
LIBDAISY_DIR ?= ../third_party/libDaisy
DAISYSP_DIR ?= ../third_party/DaisySP
SYSTEM_FILES_DIR = $(LIBDAISY_DIR)/core
APP_TYPE = BOOT_NONE
CPP_STANDARD = -std=gnu++14
C_INCLUDES += -Iinclude
ifeq ($(MIDI_BACKEND),DIN)
C_DEFS += -DPIANO_MIDI_BACKEND=0
else ifeq ($(MIDI_BACKEND),USB_INTERNAL)
C_DEFS += -DPIANO_MIDI_BACKEND=1
else
C_DEFS += -DPIANO_MIDI_BACKEND=2
endif
include $(SYSTEM_FILES_DIR)/Makefile
# Core uses one object directory; stamp enforces recompilation when switching ports.
.PHONY: FORCE
build/backend: FORCE | build
	@if test "$$(cat $@ 2>/dev/null)" != "$(MIDI_BACKEND)"; then echo $(MIDI_BACKEND) > $@; fi
build/main.o: build/backend
