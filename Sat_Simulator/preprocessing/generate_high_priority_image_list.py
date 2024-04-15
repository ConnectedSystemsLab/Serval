import json
from src.filter_graph import FilterGraph, FilterStatus, Filter
from util import build_filters
from argparse import ArgumentParser
import const
import pickle

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--sat_mapping_file",
        type=str,
        default=const.DEFAULT_IMAGE_FILE,
        help="The file that contains the mapping of satellite images to satellites",
    )
    parser.add_argument(
        "--filter_config_file", type=str, default=const.DEFAULT_FILTER_CONFIG_FILE
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
    )
    args = parser.parse_args()
    # Create the fitler graph
    filter_config = json.load(open(args.filter_config_file))
    build_filters(filter_config["filters"])
    global_filter_graph = FilterGraph(filter_config["global_filter_graph"])
    Filter.side_channel_threshold = [0, 1]  # Disable bypassing filters for ground truth
    satellite_image_mapping = pickle.load(open(args.sat_mapping_file, "rb"))[0]
    high_priority_images = []
    for satellite_id in satellite_image_mapping:
        for image in satellite_image_mapping[satellite_id]:
            FilterGraph.init_image(image)
            status = FilterStatus.RUNNING
            while status == FilterStatus.RUNNING:
                status, side_results = FilterGraph.apply_on_image(image)
                for side_result in side_results:
                    high_priority_images.append(side_result.name)
            if status == FilterStatus.COMPLETE_HI:
                high_priority_images.append(image.name)
    pickle.dump(high_priority_images, open(args.output_file, "wb+"))
