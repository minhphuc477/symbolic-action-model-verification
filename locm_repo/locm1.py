'''
| Implementation of LOCM algorithm based on paper: Acquiring planning domain models using LOCM. Cresswell, S.N., McCluskey, T.L. and   | West, M.M.,2013. The Knowledge Engineering Review, 28(2), pp.195-213.
| 
| Serawork WALLELIIGN, LIG lab/ Marven Team, France, 2022.
'''

import os, re
from copy import deepcopy, copy
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph 
import matplotlib.pyplot as plt
from action import Action
from sort import *
from state import *
from transtion import *
from hypo import *
from training_filter import *

#===================================================================================
# Takes file/files containing sequence of actions. If multiple files they should 
# be sorted according to the length of sequence in ascending order.  
#===================================================================================

path = "Training sequence/"
allSort={}
cnt =0
fs = os.listdir(path)
files = []
for f in fs:
    if f.endswith(".txt"):
        l = f.split('.')
        files.append(int(l[0]))
n=1
toRemove = training_filter(path, files)
files = [x for x in files if x not in toRemove]

#===========================================
# Step 1: Induction of Finite State Machines
#===========================================

for file in sorted(files):
    if cnt>=n:
        break
    actions = []
    sorts = {}
    filename = path + str(file) + ".txt"
    #print(file)
    if filename.endswith(".txt"):
        with open(filename) as f:
            lines = f.readlines()
    for line in lines:
        #line = re.sub(r'[()]', '', line)
        #line = line.split()
        #actions.append(Action(line[0], line[1:]))
        act = line[:line.index("(")]
        parms = line[line.index("(")+1:line.index(")")].split(",")
        actions.append(Action(act, parms))
    for i in range(len(actions)):
        params1 = actions[i].parameters
        for k in range(len(params1)):
            name = actions[i].name + "-" + str(k)
            if name in sorts.keys():
                if params1[k] not in sorts[name].objects:
                    sorts[name].addObject(params1[k])
            else:
                notc=False
                for srt in sorts.keys():
                    if params1[k] in sorts[srt].objects:
                        notc= notc or True
                if not notc:
                    sorts[name] = Sort(name, set([params1[k]]))
        for j in range(i+1, len(actions)):
            if actions[i].name == actions[j].name:
                params2 = actions[j].parameters
                for k in range(len(params2)):
                    name = actions[i].name + "-" + str(k)
                    if name in sorts.keys():
                        if params2[k] not in sorts[name].objects:
                            sorts[name].addObject(params2[k])
                    else:
                        for srt in sorts.keys():
                            if params1[k] in sorts[srt].objects:
                                sorts[srt].addObject(params2[k])
    nam = list(sorts.keys())

    while True:
        for i in nam:
            toRemove =[]
            sort1 ={}
            for j in nam:
                if i == j or j in toRemove:
                    continue
                if bool(set(sorts[j].objects).intersection(set(sorts[i].objects))):
                    sorts[i].objects = set(sorts[j].objects).union(set(sorts[i].objects))
                    toRemove.append(j)
                elif set(sorts[j].objects).issubset(set(sorts[i].objects)):
                    toRemove.append(j)
            nam = [k for k in nam if k not in toRemove]
            for k in nam:
                sort1[k] = Sort(k, sorts[k].objects)
            sorts = sort1
            nam = list(sorts.keys())
            if toRemove:
                break
        if not toRemove:
            break 
    
    nam = list(sorts.keys())
    sort1 ={}
    for i in nam:
        obj = sorted(list(sorts[i].objects))
        sort1[obj[0]] = Sort(obj[0], set(obj))
    
    sorts = sort1
    if len(allSort)==0 or allSort!=sorts:
        allSort=sorts
        cnt=0
        n=file
    elif allSort==sorts:
        cnt+=1

for i in sorts.keys():
    print(i, sorts[i].objects)
print("===========================")

#==================================================
# Step 2: Zero analysis to capture implicit objects
#==================================================


allTS=set()
cnt = 0
ActSeq=[]
for file in sorted(files):
    if cnt>=n:
        break
    actions = []
    osf = set()
    TS = []
    actions = []
    filename = path + str(file) + ".txt"
    print(file)
    if filename.endswith(".txt"):
        with open(filename) as f:
            lines = f.readlines()
    for line in lines:
        #line = re.sub(r'[()]', '', line)
        #line = line.split()
        #actions.append(Action(line[0], line[1:]))
        act = line[:line.index("(")]
        parms = line[line.index("(")+1:line.index(")")].split(",")
        actions.append(Action(act, parms))

    ActSeq.append(actions)
    sorts["dummy"]=Sort("dummy", set(["dummy"]))
    for i in actions:
        i.parameters.append("dummy")
        for j in range(len(i.parameters)):
            for k in sorts.keys():
                srt = sorts[k].objects
                if i.parameters[j] in srt:
                    sort = k
                    break
            start = ObjectState("s-"+ i.name +"."+ str(j+1), sort=sort)
            end = ObjectState("e-" + i.name +"."+ str(j+1), sort=sort)
            name = i.name +"."+ str(j+1)
            ts = Transition(name, i, i.parameters[j], sort, start, end)
            if ts not in TS:
                TS.append(ts)

    
    for s in sorts.keys():
        for k in sorts[s].objects:
            for i in range(len(actions)):
                for j in range(i+1, len(actions)):
                    if k in actions[i].parameters and k in actions[j].parameters and actions[i]!=actions[j]:
                        ind1 = actions[i].parameters.index(k) + 1
                        ind2 = actions[j].parameters.index(k) + 1
                        trans1 = Transition(actions[i].name +"."+ str(ind1), i, k, s)
                        trans2 = Transition(actions[j].name +"."+ str(ind2), j, k, s)
                        for ts in TS:
                            if trans1==ts:
                                id1 = TS.index(ts) 
                            if trans2==ts:
                                id2=TS.index(ts)
                        end = TS[id1].end
                        TS[id1].update(end=TS[id2].start)
                        for l in range(len(TS)):
                            if TS[l].start==end:
                                TS[l].update(start=TS[id2].start)
                            if TS[l].end==end:
                                TS[l].update(end=TS[id2].start)
                        break

    dummy_osf = set()
    for j in TS:
        if j.obj=="dummy":
            dummy_osf.add(j.start)
            dummy_osf.add(j.end)
    
    if len(list(dummy_osf))==1:
        for j in TS:
            if j.obj=="dummy":
                TS.remove(j)
        for i in actions:
            i.parameters.remove("dummy")
        del sorts["dummy"]
    
    #======================================
    # Renaming object states for clarity
    #======================================
    for i in sorts.keys():
        term=True
        while term:
            act=[]
            for ts in TS:
                if ts.obj in sorts[i].objects and (ts.start.name.startswith(("s", "e")) or ts.end.name.startswith(("s", "e"))):
                    act.append(ts.name)
            act = sorted(act)
            if act:
                start=None
                end=None
                for l in range(len(TS)):
                    if TS[l].name==act[0] and TS[l].obj in sorts[i].objects:
                        if TS[l].start.name.startswith(("s", "e")):
                            start = TS[l].start
                            TS[l].start.rename("ns-" + act[0])
                        if TS[l].end.name.startswith(("s", "e")):
                            end = TS[l].end
                            TS[l].end.rename("ne-" + act[0])
                for ll in range(len(TS)):
                    if end:
                        if TS[ll].start==end:
                            TS[ll].start.rename("ne-" + act[0])
                        if TS[ll].end==end:
                            TS[ll].end.rename("ne-" + act[0])
                    if start:
                        if TS[ll].start==start:
                            TS[ll].start.rename("ns-" + act[0])
                        if TS[ll].end==start:
                            TS[ll].end.rename("ns-" + act[0])
            else:
                term=False

    
    if len(allTS)==0 or allTS!=set(TS):
        allTS=set(TS)
        cnt=0
        n=file
    elif allTS==set(TS):
        cnt+=1
    print(cnt)
    print("===========================")
"""
for i in sorts.keys():
    print(i)
    for j in TS:
        if j.obj in sorts[i].objects:
            print(j.start.name, "========>", j.name, "========>", j.end.name)
"""
for i in range(len(TS)):
    osf.add(TS[i].start)
    osf.add(TS[i].end)

#=========================================
# Step 3: Induction of Parameterised FSMs
#=========================================
hypo = []
for i in range(len(TS)):
    for j in range(len(TS)):
        if TS[i].end==TS[j].start and TS[i].action!=TS[j].action:
            k = TS[i].action.parameters.index(TS[i].obj)
            kk = TS[j].action.parameters.index(TS[j].obj)
            if TS[i].sort==TS[j].sort:
                for l in range(len(TS[i].action.parameters)):
                    trans1= TS[i].action.name +"."+ str(l+1)
                    trans1 = TS[TS.index(trans1)]
                    if trans1 in TS:
                        for ll in range(len(TS[j].action.parameters)):
                            trans2 = TS[j].action.name +"."+ str(ll+1)
                            trans2 = TS[TS.index(trans2)]
                            if trans2 in TS:
                                if trans1.sort == trans2.sort and l!=k and kk!=ll:
                                    hypo.append(Hypothesis(TS[i].end, TS[i].action, k, l, TS[j].action, kk, ll, TS[i].sort, trans1.sort))

print(len(hypo))


toRemove=[]
nHypo=copy(hypo)
print(hypo==nHypo)
for k in sorts.keys():
    srt = sorts[k].objects
    for obj in srt:
        for actions in ActSeq:
            for i in range(len(actions)):
                for j in range(i+1, len(actions)):
                    if actions[i] != actions[j] and obj in actions[i].parameters and obj in actions[j].parameters:
                        for hy in hypo:
                            if actions[i] == hy.action1 and actions[j]==hy.action2 and hy.obj11==actions[i].parameters.index(obj) and hy.obj21==actions[j].parameters.index(obj):
                                if actions[i].parameters[hy.obj12]==actions[j].parameters[hy.obj22]:
                                    hy.flag=True
                                else:
                                    hy.flag=False
                                    nHypo.remove(hy)
                                    toRemove.append(hy)
                        hypo = copy(nHypo)
                        break


nHypo=[]
for hy in hypo:
    if hy.flag==True and hy not in toRemove:
        nHypo.append(hy)


hypo = deepcopy(nHypo)

#=======================================================
# Step 4 and 5: Creation and merging of state parameters
#=======================================================


i=0
for hy in hypo:
    cnt=0
    for h2 in hypo:
        if hy!=h2 and hy.is_equal(h2):
            cnt+=1
            if hy.para!=None and h2.para==None:
                h2.set_parameter(hy.para)
            if hy.para==None and h2.para!=None:
                hy.set_parameter(h2.para)
            if hy.para==None and h2.para==None:
                h2.set_parameter("V" + str(i))
                hy.set_parameter("V" + str(i))
                i+=1
    if cnt==0:
        hy.set_parameter("V" + str(i))
        i+=1

for ob in osf:
    for hy in hypo:
        if hy.S==ob:
            ob.set_parameter(hy.para + " -" + hy.sort2)

for ob in osf:
    act = []
    hyss=[]
    for ts in TS:
        if ts.end==ob:
            act.append([ts.action, ts.action.parameters.index(ts.obj)])
    for hy in hypo:
        if hy.S==ob and [hy.action1, hy.obj11] in act:
            cnt=0
            for param in ob.param:
                if hy.para in param:
                    cnt+=1
            if cnt==0:    
                hy.flag = False
print(len(hypo))
                    
nHypo = []
for hy in hypo:
    if hy.flag==True:
        nHypo.append(hy)

hypo = deepcopy(nHypo)
print(len(hypo))

for i in sorts.keys():
    print(i)
    for j in TS:
        if j.obj in sorts[i].objects:
            print(j.start.name, "========>", j.name, "========>", j.end.name)
    for hy in hypo:
        if hy.sort1==i:
            print(hy.S, hy.action1, hy.obj11, hy.obj12, hy.action2, hy.obj21, hy.obj22, hy.sort1, hy.sort2, hy.para)

#=============================================
# Step 6: Extraction of static preconditions
# Not implemented 
#=============================================

print("========")
def empty_directory(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

graphs = []
for sort in sorts.keys():
    graphs.append(nx.MultiDiGraph())
    for j in TS:
        if j.obj in sorts[sort].objects:
            node = j.start.name
            if node not in graphs[-1].nodes:
                graphs[-1].add_node(node)
            node_e=j.end.name
            if node_e not in graphs[-1].nodes:
                graphs[-1].add_node(node_e)
            graphs[-1].add_edge(node, node_e, l=j.name)

domain_name = "Blocksworld" #TO-DO extract domain name from project name

# make directory if doesn't exist
dirName = "output/"+ domain_name

if not os.path.exists(dirName):
    os.makedirs(dirName)
    print("Directory ", dirName, " Created ")
else:
    print("Directory ", dirName, " already exists")
empty_directory(dirName)


def save(graphs, domain_name, class_names):
    for index, G in enumerate(graphs):
        fig = plt.figure()
        nx.write_graphml(G, "output/"+ domain_name + "/" +  class_names[index] + ".graphml")

        G.graph['edge'] = {'arrowsize': '0.6', 'splines': 'curved'}
        G.graph['graph'] = {'scale': '10'}
        A = to_agraph(G) 
        A.layout('dot')                                                                 
        A.draw("output/"+ domain_name + "/" + class_names[index]+'.png')   
# save all the graphs
save(graphs, domain_name, list(sorts.keys())) 

#===========================
# Step 7: Formation of PDDL
#===========================

fname = "output/"+ domain_name + "/" +  domain_name + ".pddl"
with open(fname, "w") as text_file:
    text_file.write("(define (" + domain_name + ")")
    text_file.write("\n")
    text_file.write("(:requirements :strips :typing)")
    text_file.write("\n")
    text_file.write("\t" + "(:types ")
    for i in sorts.keys():
        text_file.write(i + " ")
    text_file.write("-object")
    text_file.write("\n")
    text_file.write("(:predicates ")
    for ob in osf:
        text_file.write("(" + ob.name)
        for j in ob.param:
            text_file.write(" ?"+ j)
        text_file.write(")" + "\n")
    
    acc = []
    for ts in TS:
        preco =set()
        eff=set()
        action = ts.action
        if action not in acc:
            acc.append(ts.action)
            preco.add(ts.start)
            eff.add(ts.end)
            for t in TS:
                if t!=ts and t.action==action:
                    preco.add(t.start)
                    eff.add(t.end)
            text_file.write("\n")
            text_file.write("(:action " + action.name + "\n")
            text_file.write(":parameters (")
            x=0
            parameters = {}
            preco = [ob for ob in osf if ob in preco]

            eff = [ob for ob in osf if ob in eff]
            for i in range(len(action.parameters)):
                for k in sorts.keys():
                    if action.parameters[i] in sorts[k].objects:
                        srt = k
                if i==0:
                    name = "?x" + str(x)
                    text_file.write(name + " -" + srt)
                else:
                    name = "?x" + str(x)
                    text_file.write(" " + name + " -" + srt)
                x+=1
                parameters[name] = srt
            text_file.write(")\n")
            text_file.write(":precondition (and")
            print(action.name, preco, eff)
            for pre in preco:
                text_file.write(" (" + pre.name)
                print(pre, pre.param)
                for j in pre.param:
                    text_file.write(" ?" +j) 
                text_file.write(")")
            text_file.write(")\n")
            text_file.write(":effect (and")


            for ef in eff:
                if ef not in preco:
                    text_file.write(" (" + ef.name)
                    for j in ef.param:
                        text_file.write(" ?" + j)
                    text_file.write(")")
            text_file.write(")\n")                    
            for pre in preco:
                if pre not in eff:
                    text_file.write("(not (" + pre.name)
                    for j in pre.param:
                        text_file.write(" ?" + j) 
                    text_file.write(")")
            text_file.write(")))\n")
