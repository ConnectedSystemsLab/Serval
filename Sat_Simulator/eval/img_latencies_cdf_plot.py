from argparse import ArgumentParser
import os
import pickle
from matplotlib import pyplot as plt
from loggingCode.overallLog import get_str

from eval.util import get_cdf


def parse_log_file(log_file_full_path):
    capture_time, cloud_receive_time, ground_receive_time = {}, {}, {}

    rows = get_str(log_file_full_path, "Image captured by sat")
    capture_time = {row["imageName"]: row["time"] for row in rows}


    rows = get_str(log_file_full_path, "Data Center Received data")
    cloud_receive_time = {row["imageName"]: row["time"] for row in rows}

    for name in cloud_receive_time:
        if name not in capture_time:
            # It is a data digest, look for its image
            # By removing the suffix "_vessel_digest"
            name = get_base_name(name)
            assert name in capture_time, f"{name} not in capture_time in {log_file_full_path}"
            capture_time[name+'_vessel_digest'] = capture_time[name]

    rows = get_str(log_file_full_path, "Processing data object")
    ground_receive_time = {row["imageName"]: row["time"] for row in rows}
    for name in cloud_receive_time:
        if name not in ground_receive_time:
            # It is a data digest that is generated on ground, look for its image
            # By removing the suffix "_vessel_digest"
            name = get_base_name(name)
            assert name in capture_time, f"{name} not in capture_time in {log_file_full_path}"
            ground_receive_time[name+'_vessel_digest'] = ground_receive_time[name]

    return capture_time, cloud_receive_time, ground_receive_time

def get_base_name(image_name): # remove suffix like _vessel_digest for data digest
    if image_name.endswith("_vessel_digest"):
        return image_name[:-len("_vessel_digest")]
    return image_name

def main():
    parser = ArgumentParser()
    parser.add_argument("--log_folder", type=str, required=True,
                        help="The folder that contains the list of images uploaded to the cloud")
    parser.add_argument("--output_file", type=str,
                        required=True, help="The output file")
    parser.add_argument("--high_priority_ground_truth_file", type=str, required=True)
    args = parser.parse_args()
    # All latencies
    log_record={}
    for log_file in os.listdir(args.log_folder):
        capture_time, cloud_receive_time, ground_receive_time = parse_log_file(os.path.join(args.log_folder, log_file))
        log_record[log_file]={
            "capture_time": capture_time,
            "cloud_receive_time": cloud_receive_time,
            "ground_receive_time": ground_receive_time,
        }
    high_priority_ground_truth = pickle.load(open(args.high_priority_ground_truth_file, "rb"))
    # Only keep the images that are in all the log files' cloud_receive_time
    common_image_list = set(log_record[list(log_record.keys())[0]]["cloud_receive_time"].keys())
    for name in log_record:
        common_image_list = common_image_list.intersection(set(log_record[name]["cloud_receive_time"].keys()))
    for name in log_record:
        log_record[name]["cloud_receive_time"] = {k: v for k, v in log_record[name]["cloud_receive_time"].items() if k in common_image_list}
        log_record[name]["ground_receive_time"] = {k: v for k, v in log_record[name]["ground_receive_time"].items() if k in common_image_list}
        log_record[name]["capture_time"] = {k: v for k, v in log_record[name]["capture_time"].items() if k in common_image_list}
    
    # Latencies for all images
    for name in log_record:
        all_image_latencies = []
        for image_name in log_record[name]["cloud_receive_time"]:
            latency=log_record[name]["cloud_receive_time"][image_name] - log_record[name]["capture_time"][image_name]
            latency=latency.total_seconds()/3600
            all_image_latencies.append(latency)
        indices, cdf = get_cdf(all_image_latencies)
        plt.plot(indices, cdf, label=name)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlabel("Latency (hours)")
    plt.xscale("log")
    plt.ylabel("CDF")
    plt.savefig(args.output_file+"_all.pdf", bbox_inches='tight')
    plt.clf()

    # Latencies for high priority images
    for name in log_record:
        high_priority_image_latencies = []
        for image_name in log_record[name]["cloud_receive_time"]:
            if image_name not in high_priority_ground_truth:
                continue
            latency=log_record[name]["cloud_receive_time"][image_name] - log_record[name]["capture_time"][image_name]
            latency=latency.total_seconds()/3600
            high_priority_image_latencies.append(latency)
        indices, cdf = get_cdf(high_priority_image_latencies)
        plt.plot(indices, cdf, label=name)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlabel("Latency (hours)")
    plt.xscale("log")
    plt.ylabel("CDF")
    plt.savefig(args.output_file+"_high_priority.pdf", bbox_inches='tight')
    plt.clf()

    # Latencies for all images on satellite
    for name in log_record:
        all_image_latencies = []
        for image_name in log_record[name]["ground_receive_time"]:
            latency=log_record[name]["ground_receive_time"][image_name] - log_record[name]["capture_time"][image_name]
            latency=latency.total_seconds()/3600
            all_image_latencies.append(latency)
        indices, cdf = get_cdf(all_image_latencies)
        plt.plot(indices, cdf, label=name)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlabel("Latency (hours)")
    plt.xscale("log")
    plt.ylabel("CDF")
    plt.savefig(args.output_file+"_satellite.pdf", bbox_inches='tight')
    plt.clf()

    # Latencies for high priority images on satellite
    for name in log_record:
        high_priority_image_latencies = []
        for image_name in log_record[name]["ground_receive_time"]:
            if image_name not in high_priority_ground_truth:
                continue
            latency=log_record[name]["ground_receive_time"][image_name] - log_record[name]["capture_time"][image_name]
            latency=latency.total_seconds()/3600
            high_priority_image_latencies.append(latency)
        indices, cdf = get_cdf(high_priority_image_latencies)
        plt.plot(indices, cdf, label=name)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlabel("Latency (hours)")
    plt.xscale("log")
    plt.ylabel("CDF")
    plt.savefig(args.output_file+"_satellite_high_priority.pdf", bbox_inches='tight')
    plt.clf()

    # Latencies for all images on ground
    for name in log_record:
        all_image_latencies = []
        for image_name in log_record[name]["cloud_receive_time"]:
            latency=log_record[name]["cloud_receive_time"][image_name] - log_record[name]["ground_receive_time"][image_name]
            latency=latency.total_seconds()/3600
            all_image_latencies.append(latency)
        indices, cdf = get_cdf(all_image_latencies)
        plt.plot(indices, cdf, label=name)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlabel("Latency (hours)")
    plt.xscale("log")
    plt.ylabel("CDF")
    plt.savefig(args.output_file+"_ground.pdf", bbox_inches='tight')
    plt.clf()

    # Latencies for high priority images on ground
    for name in log_record:
        high_priority_image_latencies = []
        for image_name in log_record[name]["cloud_receive_time"]:
            if image_name not in high_priority_ground_truth:
                continue
            latency=log_record[name]["cloud_receive_time"][image_name] - log_record[name]["ground_receive_time"][image_name]
            latency=latency.total_seconds()/3600
            high_priority_image_latencies.append(latency)
        indices, cdf = get_cdf(high_priority_image_latencies)
        plt.plot(indices, cdf, label=name)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlabel("Latency (hours)")
    plt.xscale("log")
    plt.ylabel("CDF")
    plt.savefig(args.output_file+"_ground_high_priority.pdf", bbox_inches='tight')
    plt.clf()



if __name__ == "__main__":
    main()
