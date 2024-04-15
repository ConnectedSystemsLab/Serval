import os
import json

config_dir = "data/gs_config/"

for filename in os.listdir(config_dir):
    if filename.endswith(".json"):
        with open(config_dir + filename, 'r') as f:
            config = json.load(f)

        new_config = {}

        for key, value in config.items():
            for i in range(4):
                new_key = f"{int(key)+i*len(config)}"  # generate unique key for each station
                new_name = f"Ground Station {int(key)+i*len(config)+1}"  # generate unique name for each station
                new_config[new_key] = {"name": new_name, "position": value["position"], "bandwidth": value["bandwidth"]}

        with open(config_dir + filename, 'w') as f:
            json.dump(new_config, f, indent=2)
