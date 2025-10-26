#!/bin/bash

DATASET_PATH="$1"
DATASET_NAME="$2"
SCRIPT="scalability/scalability.py"  # Replace with your actual script
QUERY_FILE="../queries/${DATASET_NAME}.txt"

# Check for query file
if [ ! -f "$QUERY_FILE" ]; then
    echo "Query file $QUERY_FILE not found!"
    exit 1
fi

# Read the first 32 queries
mapfile -t queries < <(sed -n '1,15p' "$QUERY_FILE")
# Launch each query in a separate tmux session, pinned to a different core
for core in $(seq 0 30); do
    query_line="${queries[$core]}"
    
    # Skip if empty
    if [ -z "$query_line" ]; then
        echo "Less than 31 queries. Stopping at core $core."
        break
    fi

    # Parse CSV: query_file, query_column, selectivity
    IFS='.' read -r query_file query_column selectivity <<< "$query_line"

    session_name="core$core"
    echo "Launching $session_name → File: $query_file, Column: $query_column, Selectivity: $selectivity, Data_path: $DATASET_PATH, Data_name: $DATASET_NAME"

    tmux new-session -d -s "$session_name" \
        "taskset -c $core python3 $SCRIPT \
        --dataset_name $DATASET_NAME \
        --query_file \"${query_file}.csv\" \
        --query_column \"${query_column}\" \
        --dataset_path $DATASET_PATH"
done
