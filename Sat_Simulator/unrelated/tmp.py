infile = r"ours10-.25-.15-.005.log"

important = []
keep_phrases = ["test",
              "important",
              "keep me"]

with open(infile) as f:
    f = f.readlines()

consumption_sum =0
consumption_ct = 0

transmitting = 0
transmitting_ct=0
for line in f:
    if "Consumption" in line:
        consumption_sum += float(line.split("\t")[-1])
        consumption_ct +=1
    if "Power transmitting" in line and not "Iot" in line:
        transmitting += float(line.split("\t")[-1])
        transmitting_ct+=1

consumption_mean = consumption_sum/consumption_ct
transmitting_mean = transmitting/transmitting_ct
print(consumption_mean - transmitting_mean)
