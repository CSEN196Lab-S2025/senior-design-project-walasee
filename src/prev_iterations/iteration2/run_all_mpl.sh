#!/bin/bash

# Path to the text file containing filenames
filenames_file="filenames.txt"

# Check if the filenames file exists
if [ -f "$filenames_file" ]; then
    # Read each filename from the file and process
    while IFS= read -r filename; do
        # Print filename being processed
        echo "Processing file: $filename"

        # Update the file_path variable in your Python script
        sed -i "s|file_path = .*|file_path = \"$filename\"|" plotting.ipynb
        # Run your Python script
        python plotting.ipynb

    done < "$filenames_file"
else
    echo "Error: File '$filenames_file' not found."
fi
