import os
from matplotlib import pyplot as plt
import numpy as np
from loggingCode.overallLog import get_str


def get_latencies(img_list):
    return [(img.receved_time - img.time).total_seconds() for img in img_list]


def get_cdf(values):
    values = np.sort(values)
    p = 1.0 * np.arange(len(values)) / (len(values) - 1)
    return values, p


def parse_log_file(log_file_full_path):
    capture_time, cloud_receive_time, ground_receive_time = {}, {}, {}

    rows = get_str(log_file_full_path, "Image captured by sat")
    capture_time = {row["imageName"]: row["time"] for row in rows}

    rows = get_str(log_file_full_path, "Data Center Received data")
    cloud_receive_time = {row["imageName"]: row["time"] for row in rows if "OEC" not in row["imageName"]}

    for name in cloud_receive_time:
        if name not in capture_time:
            # It is a data digest, look for its image
            # By removing the suffix "_vessel_digest"
            name = get_base_name(name)
            assert (
                name in capture_time
            ), f"{name} not in capture_time in {log_file_full_path}"
            capture_time[name + "_vessel_digest"] = capture_time[name]

    rows = get_str(log_file_full_path, "Processing data object")
    ground_receive_time = {row["imageName"]: row["time"] for row in rows}
    for name in cloud_receive_time:
        if name not in ground_receive_time:
            # It is a data digest that is generated on ground, look for its image
            # By removing the suffix "_vessel_digest"
            name = get_base_name(name)
            assert (
                name in capture_time
            ), f"{name} not in capture_time in {log_file_full_path}"
            ground_receive_time[name + "_vessel_digest"] = ground_receive_time[name]

    return capture_time, cloud_receive_time, ground_receive_time


def get_base_name(image_name):  # remove suffix like _vessel_digest for data digest
    if image_name.endswith("_vessel_digest"):
        return image_name[: -len("_vessel_digest")]
    return image_name


def process_hardware_dir(
    hardware_dir, result_dir, high_priority_ground_truth, priority_only=False, save_figure=True
):
    hardware_name = hardware_dir.split("/")[-1]
    _log_record = {}
    for log_file in os.listdir(hardware_dir):
        log_file_full_path = os.path.join(hardware_dir, log_file)
        capture_time, cloud_receive_time, ground_receive_time = parse_log_file(
            log_file_full_path
        )
        _log_record[log_file] = {
            "capture_time": capture_time,
            "cloud_receive_time": cloud_receive_time,
            "ground_receive_time": ground_receive_time,
        }
    plt.figure(figsize=(5, 4))
    percentile_values = {}
    plot_record = {}
    for name in _log_record:
        percentile_values[name] = {}
        if not priority_only:
            image_latencies = []
            for image_name in _log_record[name]["cloud_receive_time"]:
                latency = (
                    _log_record[name]["cloud_receive_time"][image_name]
                    - _log_record[name]["capture_time"][image_name]
                )
                latency = latency.total_seconds() / 3600
                image_latencies.append(latency)
            percentile_values[name]["all"] = {
                "50": np.percentile(image_latencies, 50),
                "90": np.percentile(image_latencies, 90),
            }
            indices, cdf = get_cdf(image_latencies)
            plt.plot(indices, cdf, label=f"{name}")
            plot_record[name] = [indices, cdf]
        high_priority_image_latencies = []
        for image_name in _log_record[name]["cloud_receive_time"]:
            if image_name not in high_priority_ground_truth:
                continue
            latency = (
                _log_record[name]["cloud_receive_time"][image_name]
                - _log_record[name]["capture_time"][image_name]
            )
            latency = latency.total_seconds() / 3600
            high_priority_image_latencies.append(latency)
        indices, cdf = get_cdf(high_priority_image_latencies)
        percentile_values[name]["high_priority"] = {
            "50": np.percentile(high_priority_image_latencies, 50),
            "90": np.percentile(high_priority_image_latencies, 90),
        }
        plt.plot(indices, cdf, label=f"{name} (high priority)")
        plot_record[name + " (high priority)"] = [indices, cdf]
    plt.legend()
    plt.xlabel("Latency (hour)")
    plt.ylabel("CDF")
    plt.xscale("log")
    plt.grid()
    if save_figure:
        plt.savefig(
            os.path.join(result_dir, f"{hardware_name}_latency_cdf.pdf"),
            bbox_inches="tight",
            dpi=300,
        )
    plt.clf()
    with open(os.path.join(result_dir, f"{hardware_name}_latency.csv"), "w") as f:
        f.write("image_name,name,50,90\n")
        for name in percentile_values:
            for image_name in percentile_values[name]:
                f.write(
                    f"{image_name},{name},{percentile_values[name][image_name]['50']},{percentile_values[name][image_name]['90']}\n"
                )
    return plot_record
