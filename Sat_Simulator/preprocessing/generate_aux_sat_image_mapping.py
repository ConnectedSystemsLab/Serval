import argparse
import pickle

parser = argparse.ArgumentParser(description="Modify runtime values in pickle file")
parser.add_argument("input_file", help="input pickle file")
parser.add_argument("output_file_zero", help="output pickle file with runtime values set to 0")
parser.add_argument("output_file_max", help="output pickle file with runtime values set to 9999999")
args = parser.parse_args()

with open(args.input_file, "rb") as f:
    data = pickle.load(f)

# Modify runtime values to 0
for img_list in data[0].values():
    for img in img_list:
        for filter_name in img.filter_result:
            img.filter_result[filter_name][1] = 0

with open(args.output_file_zero, "wb+") as f:
    pickle.dump(data, f)

# Modify runtime values to 9999999
for img_list in data[0].values():
    for img in img_list:
        for filter_name in img.filter_result:
            img.filter_result[filter_name][1] = 9999999

with open(args.output_file_max, "wb+") as f:
    pickle.dump(data, f)
