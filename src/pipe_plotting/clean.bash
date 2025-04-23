#!/bin/bash

# Usage: ./extract_hits.sh input.txt > hits.txt

while IFS= read -r line; do
    if [[ ! "$line" =~ ^No\ Target\ Detected\ at ]]; then
        echo "$line" | sed -E 's/cm//g; s/x: //; s/y: //; s/z: //; s/a:.*//'
    fi
done < "$1"

