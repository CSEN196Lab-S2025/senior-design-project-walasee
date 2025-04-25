#!/bin/bash

# Directory containing the XYZ text files
DATA_DIR="walabotOut_txt"
PYTHON_SCRIPT="plot.py"  # Your Python plotting script
OUTPUT_DIR="outputs"  # Directory to store output plots

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Ensure the data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Directory '$DATA_DIR' not found!"
    exit 1
fi

# Loop through all .txt files in the directory
for file in "$DATA_DIR"/*.txt; do
    # Extract just the filename without path
    filename=$(basename "$file")

    echo "Processing file: $filename"

    # Run the Python script with the current file
    python3 "$PYTHON_SCRIPT" "$file"

done

echo "Processing complete! All outputs saved in '$OUTPUT_DIR'."

