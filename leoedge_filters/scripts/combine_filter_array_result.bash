#!/bin/bash

APPS=("cloud" "forest" "fire") # TODO add vessel when done
RESULTS_DIR="results/filter_results/"
OUTPUT_FILE="results/filter_results.pkl"
PYTHON_SCRIPT="preprocessing/combine_filter_array_result.py"

python "$PYTHON_SCRIPT" --apps "${APPS[@]}" --results-dir "$RESULTS_DIR" --output "$OUTPUT_FILE"
