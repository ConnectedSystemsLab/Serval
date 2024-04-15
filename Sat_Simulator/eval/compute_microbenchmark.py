import os
import pickle
import sys
import multiprocessing
from matplotlib import pyplot as plt
import seaborn as sns

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from eval.util import get_cdf, get_latencies, parse_log_file
from eval.forest_microbenchmark import process_hardware_dir



if __name__ == "__main__":
    log_base_dir = "log/compute/dgs_001"
    sns.set_theme()
    high_priority_ground_truth = pickle.load(
        open("data/high_priority_list.pkl", "rb")
    )

    plot_record=process_hardware_dir(log_base_dir,'results/compute', high_priority_ground_truth, True)
    pickle.dump(plot_record, open("results/compute.pkl", "wb+"))

