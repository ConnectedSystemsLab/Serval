
#let's parse and make a plot of the power data
import matplotlib.pyplot as plt
import pandas as pd

#parse the data - the first 15 lines are header info - each line is a data point following the order of the header
f = open("power.txt", "r")
lines = f.readlines()
f.close()

#let's convert the lines to a csv
"""
for i in range(len(lines)):
    lines[i].replace(" ", "")
    lines[i].replace("\t", "")
    lines[i] = lines[i].replace("\n", ",")
    if i % 15 == 14:
        #if the next line is a time, then we need to add a newline
        if lines[i+1][0:5] == "2022":
            lines[i] = lines[i].replace(",", "\n")
"""
#if the next line is a time, then we need to add a newline
for i in range(len(lines) - 1):
    lines[i] = lines[i].replace(" ", "")
    lines[i] = lines[i].replace("\t", "")
    lines[i] = lines[i].replace("\n", ",")
    if lines[i+1][0:3] == "05/":
        lines[i] = lines[i].replace(",", "\n")
#write the csv
f = open("power.csv", "w")
f.writelines(lines)
f.close()
