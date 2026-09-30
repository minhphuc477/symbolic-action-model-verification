import os, re
from copy import deepcopy
from action import Action

def training_filter(path, files):
    allSort=set()
    missing_f = []
    n=1
    for file in sorted(files):
        allSort1=set()
        actions = []
        filename = path + str(file) + ".txt"
        #print(file)
        if filename.endswith(".txt"):
            with open(filename) as f:
                lines = f.readlines()
        for line in lines:
            line = re.sub(r'[()]', '', line)
            line = line.split()
            #print(line)
            actions.append(Action(line[0], line[1:]))
        for i in range(len(actions)):
            params1 = actions[i].parameters
            for k in range(len(params1)):
                allSort1.add(params1[k])

        allSort = allSort.union(allSort1)
        missing_obj = allSort.difference(allSort1)
        if len(missing_obj)!=0:
            #print("Please add action containing object ", missing_obj)
            missing_f.append(file)
    return missing_f
