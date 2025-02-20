#!/bin/bash

# Find the most recent .html file
latest_html=$(ls -t *.html 2>/dev/null | head -n 1)

# Check if a file was found
if [[ -z "$latest_html" ]]; then
    echo "No HTML files found in the current directory."
    sleep 5
    exit 1
fi

# Run the Python script with the latest HTML file
molprobity_to_coot.py --column "Ramachandran" --filter_text "OUTLIER" "$latest_html"

# Delay for 5 seconds before closing
sleep 5
