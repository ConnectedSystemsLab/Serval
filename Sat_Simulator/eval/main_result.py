import os
import pickle
import sys
import multiprocessing
import seaborn as sns

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from eval.util import process_hardware_dir


if __name__ == "__main__":
    log_base_dir = "log/main"
    sns.set_theme()
    high_priority_ground_truth = pickle.load(
        open("data/high_priority_list.pkl", "rb")
    )

    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_processes)

    for hardware_name in os.listdir(log_base_dir):
        hardware_dir = os.path.join(log_base_dir, hardware_name)
        plot_record=process_hardware_dir(hardware_dir,"results/main", high_priority_ground_truth)
        pickle.dump(plot_record, open(f"results/main/{hardware_name}.pkl", "wb+"))

    pool.close()
    pool.join()

