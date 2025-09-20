#!/usr/bin/env bash

# Exit on error
set -o errexit

# Update package list and install system dependencies for aiortc
apt-get update
apt-get install -y libavdevice-dev libavfilter-dev libavutil-dev libsrtp2-dev libx264-dev

# Install Python dependencies from requirements.txt
pip install -r requirements.txt