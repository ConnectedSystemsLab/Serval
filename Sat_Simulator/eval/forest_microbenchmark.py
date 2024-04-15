import os
import pickle
import sys
import multiprocessing
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from eval.util import process_hardware_dir


if __name__ == "__main__":
    log_base_dir = "log/forest/dgs_001"
    sns.set_theme()
    high_priority_ground_truth = pickle.load(
        open("data/high_priority_list.pkl", "rb")
    )
    high_priority_ground_truth=[x for x in high_priority_ground_truth if 'vessel' not in x]
    plot_record=process_hardware_dir(log_base_dir,"results/forest", high_priority_ground_truth, save_figure=False, priority_only=True)
    for name in plot_record:
        plt.plot(plot_record[name][0], plot_record[name][1], label=f"{name}")
    plt.legend()
    plt.xlabel("Latency (hours)")
    plt.ylabel("CDF")
    plt.xscale("log")
    plt.savefig("results/forest_old.pdf", dpi=300, bbox_inches='tight')
    pickle.dump(plot_record, open("results/forest_old.pkl", "wb+"))