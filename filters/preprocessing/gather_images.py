import argparse
import os

# Create the argument parser
parser = argparse.ArgumentParser(description='Recursively search for all files with a given extension under the specified directories and write their absolute paths to a file.')
parser.add_argument('-d', '--dirs', nargs='+', required=True, help='the directories to search under')
parser.add_argument('-o', '--output', required=True, help='the output file to write to')
parser.add_argument('-e', '--extension', required=True, help='the file extension to search for')
parser.add_argument('-i','--id_file',help='output the image ids to a file',default=None)

# Parse the command line arguments
args = parser.parse_args()

# Define the directories to search under
dirs_to_search = args.dirs

# Define the output file to write to
output_file = args.output

# Define the file extension to search for
file_extension = args.extension

# Open the output file for writing
with open(output_file, 'w') as f:
    # Loop over each directory to search under
    for directory in dirs_to_search:
        # Recursively search for all files with the specified extension
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    # Write the absolute path of the file to the output file
                    f.write(os.path.join(root, file) + '\n')

if args.id_file is not None:
    with open(args.id_file,'w') as f:
        for directory in dirs_to_search:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(file_extension):
                        # Write the absolute path of the file to the output file
                        filename=os.path.basename(file)
                        image_id=filename[:-len(file_extension)]
                        f.write(image_id + '\n')