#!/bin/bash
# Test script to run the Evil Crow TUI

cd "$(dirname "$0")/../tui"

# Activate venv and run
source venv/bin/activate
evilcrow
