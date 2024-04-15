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
    log_base_dir = "log/priority_sweep"
    sns.set_theme()
    high_priority_ground_truth = pickle.load(
        open("data/high_priority_list.pkl", "rb")
    )

    plot_record=process_hardware_dir(log_base_dir,"results/priority_sweep", high_priority_ground_truth, save_figure=False)
    name_mapping={
        '0.0005.log (high priority)': 'Serval 0.05%',
        '0.001.log (high priority)': 'Serval 0.1%',
        '0.005.log (high priority)': 'Serval 0.5%',
        '0.001.log': 'In-Order',
    }
    save_record={}
    for name in plot_record:
        if not "priority" in name and not "0.001" in name:
            continue
        if name not in name_mapping:
            continue
        plt.plot(plot_record[name][0], plot_record[name][1], label=f"{name_mapping[name]}")
        save_record[name_mapping[name]]=plot_record[name]
    plt.legend()
    plt.xlabel("Latency (hours)")
    plt.ylabel("CDF")
    plt.xscale("log")
    plt.savefig("results/priority_sweep.pdf", dpi=300, bbox_inches='tight')
    pickle.dump(save_record, open("results/priority_sweep.pkl", "wb+"))
