#!/bin/bash

find ./cat/plugins -type f -name "requirements.txt" | while read -r req_file; do
    pip install --no-cache-dir -r "$req_file"
done
