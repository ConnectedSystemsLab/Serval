#! /bin/bash

module load anaconda/2022-May/3
source activate torch
cd /home/yutao4/leoedge_filters || exit 255

export PYTHONPATH="/home/yutao4/leoedge_filters"
python preprocessing/gather_planet_images.py \
    --root /projects/vasishtgroup/yutao4/planet_data/ca_20day/CA_15days \
    --portion 0.01 \
    --root /projects/vasishtgroup/yutao4/planet_data/ports \
    --portion 1 \
    --output data/yolo_training_images