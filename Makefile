# Find all jp_*.txt files
TXT_FILES := $(wildcard jp_*.txt)

# Convert .txt to .mp3 targets
MP3_FILES := $(TXT_FILES:.txt=.mp3)

# Python virtual environment
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Default target
all: $(MP3_FILES)

# Install system dependencies
system-deps:
	sudo apt-get update
	sudo apt-get install -y  ffmpeg
	sudo pip3 install gtts pygame pydub numpy

# Setup virtual environment and install dependencies
setup: system-deps $(VENV)/bin/activate

$(VENV)/bin/activate: 
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install wheel

# Rule to create .mp3 from .txt
%.mp3: %.txt text_to_speech.py
	$(PYTHON) text_to_speech.py $<

# Clean up generated mp3 files and virtual environment
clean:
	rm -f *.mp3
	rm -rf $(VENV)

.PHONY: all clean setup system-deps 