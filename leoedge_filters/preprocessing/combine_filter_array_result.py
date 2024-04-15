import argparse
import os
import pickle

parser = argparse.ArgumentParser(description="Merge multiple pickle files into one.")
parser.add_argument("--apps", metavar="APP", type=str, nargs="+", required=True,
                    help="the names of the applications to merge (choose from cloud, forest, fire)")
parser.add_argument("--results-dir", metavar="DIR", type=str, default="results",
                    help="the directory where the application results are stored (default: results)")
parser.add_argument("--output", metavar="FILE", type=str, default="merged.pickle",
                    help="the file path to save the merged pickle data (default: merged.pickle)")

args = parser.parse_args()

app_names = args.apps
results_dir = args.results_dir
app_results = {}

for app in app_names:
    app_dir = os.path.join(results_dir, app)
    for filename in os.listdir(app_dir):
        if filename.endswith(".pkl"):
            filepath = os.path.join(app_dir, filename)
            with open(filepath, "rb") as f:
                app_data = pickle.load(f)
                for id_, results in app_data.items():
                    if id_ not in app_results:
                        app_results[id_] = {}
                    app_results[id_][app] = results

with open(args.output, "wb") as f:
    pickle.dump(app_results, f)
