print("importing")
import json
import pickle
import const
from argparse import ArgumentParser
import os
from datetime import datetime
from src.dataCenter import DataCenter
from src.filter_graph import FilterGraph, Filter
import src.log as log
from fastlogging import LogInit, INFO, Logger
from util import create_simulator, build_filters

print("Everything imported")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--satellite_image_mapping_file", type=str, default=const.DEFAULT_IMAGE_FILE,
                        help="The file that contains the mapping of satellite images to satellites")
    parser.add_argument("--ground_station_config_file", type=str, default=const.DEFAULT_GROUND_STATION_CONFIG_FILE,
                        help="The file that contains the ground station config")
    parser.add_argument("--start_datetime", type=lambda s: datetime.strptime(
        s, '%Y-%m-%dT%H:%M:%S'), default=const.START_TIME, help="The start datetime")
    parser.add_argument("--end_datetime", type=lambda s: datetime.strptime(
        s, '%Y-%m-%dT%H:%M:%S'), default=const.END_TIME, help="The end datetime")
    parser.add_argument("--energy_config_file", type=str,
                        default=const.DEFAULT_ENERGY_CONFIG_FILE,)
    parser.add_argument("--logging_file", type=str, default=const.LOGGING_FILE)
    parser.add_argument('--filter_config_file', type=str,
                        default=const.DEFAULT_FILTER_CONFIG_FILE)
    parser.add_argument("--priority_bw_allocation", type=float,default=const.MAX_PRIORITY_BANDWIDTH)
    parser.add_argument("--downlink_bandwidth_scaling", type=float,default=const.DOWNLINK_BANDWIDTH_SCALING)
    parser.add_argument("--cloud_threshold", type=float, nargs=2, default=const.DEFAULT_CLOUD_THRESHOLD)
    parser.add_argument("--oec", action="store_true", default=False, help="Whether to use the OEC", dest="oec")
    args = parser.parse_args()
    const.DOWNLINK_BANDWIDTH_SCALING = args.downlink_bandwidth_scaling
    const.OEC = args.oec
    log.logger = LogInit(pathName=args.logging_file,
                         level=INFO, encoding="ascii", useThreads=True)
    filter_config = json.load(open(args.filter_config_file))
    for filter_name in filter_config["filters"]:
        filter_config["filters"][filter_name]["side_channel_threshold"] = args.cloud_threshold
    build_filters(filter_config["filters"])
    global_filter_graph = FilterGraph(filter_config["global_filter_graph"])
    sim = create_simulator(args)
    print("Running simulation...")
    sim.run()
    print("Simulation complete")
