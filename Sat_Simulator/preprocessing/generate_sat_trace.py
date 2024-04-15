from datetime import datetime, timezone
import json
from src.filter_graph import FilterGraph
from src.image import Image
from util import build_filters, generate_satellite_image_mapping_dict
from argparse import ArgumentParser
import const
import pickle

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--image_file", type=str, default=const.DEFAULT_IMAGE_FILE,
                        help="The file that contains the mapping of satellite images to satellites")
    parser.add_argument("--filter_config_file", type=str,
                        default=const.DEFAULT_FILTER_CONFIG_FILE)
    parser.add_argument("--output_file", type=str, required=True,)
    parser.add_argument("--datetime_cutoff", type=str, default=None)
    args = parser.parse_args()
    datetime_cutoff = datetime.strptime(
        args.datetime_cutoff, '%Y-%m-%dT%H:%M:%S',).replace(tzinfo=timezone.utc) if args.datetime_cutoff is not None else None
    image_record = pickle.load(open(args.image_file, "rb"))
    # Create the fitler graph
    filter_config = json.load(open(args.filter_config_file))
    build_filters(filter_config["filters"])
    global_filter_graph = FilterGraph(filter_config["global_filter_graph"])
    satellite_image_mapping = generate_satellite_image_mapping_dict(
        image_record, datetime_cutoff=datetime_cutoff, image_size=const.DATA_SIZE)
    current_image_id = Image.id
    pickle.dump([satellite_image_mapping, current_image_id],
                open(args.output_file, "wb+"))
