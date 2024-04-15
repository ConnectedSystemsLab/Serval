#! /bin/bash

module load anaconda/2022-May/3
source activate torch
cd /home/yutao4/leoedge_filters || exit 255
PYTHONPATH="/home/yutao4/leoedge_filters" python experiments/inject_filter_result_into_image.py --image_file data/ca_20day/metadata_full.pkl --filter_result_file results/filter_results.pkl --output_file results/filtered_images.pkl --log_file logs/inject_filter_result_into_image.log