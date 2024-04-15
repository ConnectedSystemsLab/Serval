import sys
import os

plots = [i for i in os.listdir(os.getcwd()) if 'plot' in i and '.py' in i]

for i in plots:
    os.system("python " + i + " " + sys.argv[1])