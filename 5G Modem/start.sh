#!/bin/bash

# ============================
# CONFIG
# ============================

HOME_DIR="$HOME"
BASE_DIR="$HOME_DIR/Research/Rogers/5G"
RUNNING_DIR="$BASE_DIR/running"
CONFUSING_SCRIPT="$BASE_DIR/confusing.sh"

MODE="$1"  # uplink or downlink

if [[ "$MODE" != "uplink" && "$MODE" != "downlink" ]]; then
    echo "Usage: $0 {uplink|downlink}"
    exit 1
fi

# ============================
# STEP 1: Run confusing.sh in background
# ============================

echo "Starting confusing.sh..."
bash "$CONFUSING_SCRIPT" &
sleep 2

# ============================
# STEP 2: Create folder structure
# ============================

DATE_FOLDER=$(date +"%b_%d")  # Example: Nov_11
TARGET_DIR="$RUNNING_DIR/$DATE_FOLDER/$MODE"

mkdir -p "$TARGET_DIR"
echo "Created: $TARGET_DIR"

# ============================
# STEP 3: Copy scripts to new folder
# ============================

echo "Copying files..."
cp "$RUNNING_DIR/ping.py" "$TARGET_DIR/"

if [[ "$MODE" == "uplink" ]]; then
    cp "$RUNNING_DIR/up.py" "$TARGET_DIR/"
    SELECTED_SCRIPT="up.py"
else
    cp "$RUNNING_DIR/down.py" "$TARGET_DIR/"
    SELECTED_SCRIPT="down.py"
fi

# ============================
# STEP 4: Launch Python tasks with delay in separate terminals
# ============================

echo "Launching new terminal windows..."

# Terminal for ping.py
gnome-terminal -- bash -c "echo 'Sleeping 10...'; sleep 30; python3 '$TARGET_DIR/ping.py'; exec bash"

# Terminal for up.py or down.py
gnome-terminal -- bash -c "echo 'Sleeping 10...'; sleep 30; python3 '$TARGET_DIR/$SELECTED_SCRIPT'; exec bash"

# Extra empty terminal
gnome-terminal -- bash -c "echo 'Empty terminal ready'; exec bash"

echo "✅ All done — terminals launched with delay."

