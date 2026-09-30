from collections import defaultdict
import itertools
import os
from tabulate import tabulate
from pprint import pprint
import matplotlib.pyplot as plt
#matplotlib inline
import networkx as nx
import pandas as pd
pd.options.display.max_columns = 100
from IPython.display import display, Markdown
from ipycytoscape import *
import string



def read_input(input_seqs):
    '''
    Read the input data and return list of action sequences.
    Each sequence is a list of action-argumentlist tuples.
    '''
    sequences = []
    for seq in input_seqs.split('\n'):
        
        actions = []
        arguments = []
        if seq and not seq.isspace() and len(seq)>1:
            sequence = seq.rstrip("\n\r").lstrip("\n\r").lower() 
            action_defs = sequence.split("),")

            for action_def in action_defs:
                action = action_def.split('(')[0].strip(")\n\r").strip()
                argument = action_def.split('(')[1].strip(")\n\r")
                actions.append(action.translate(str.maketrans('', '', string.punctuation)))
                argument_list = argument.split(',')
                argument_list = [x.strip() for x in argument_list]
                argument_list.insert(0,'zero')
                arguments.append(argument_list)
                
            actarg_tuples = zip(actions,arguments)
            sequences.append(list(actarg_tuples))
    return sequences


def print_sequences(sequences):
    for seq in sequences:
        for index,action in enumerate(seq):
            print(str(index) + ": " + str(action))
        print()



def get_actarg_dictionary(sequences):
    d = defaultdict(list)
    for seq in sequences:
        for actarg_tuple in seq:
            d[actarg_tuple[0]].append(actarg_tuple[1])
    return d


# class util functions.
def get_classes(d):
    # TODO incorporate word similarity in get classes.
    c = defaultdict(set)
    for k,v in d.items():
        for arg_list in v:
            for i,object in enumerate(arg_list):
                c[k,i].add(object)

    sets = c.values()
    classes = []
    # remove duplicate classes
    for s in sets:
        if s not in classes:
            classes.append(s)

    # now do pairwise intersections of all values. If intersection, combine them; then return the final sets.
    classes_copy = list(classes)
    while True:
        combinations = list(itertools.combinations(classes_copy,2))
        intersections_count = 0
        for combination in combinations:
            if combination[0].intersection(combination[1]):
                intersections_count +=1

                if combination[0] in classes_copy:
                    classes_copy.remove(combination[0])
                if combination[1] in classes_copy:
                    classes_copy.remove(combination[1])
                classes_copy.append(combination[0].union(combination[1]))

        if intersections_count==0:
            # print("no intersections left")
            break

    return classes_copy

# TODO: Can use better approach here. NER might help.
def get_class_names(classes):
    # Name the class to first object found ignoring the digits in it
    class_names = []
    for c in classes:
        for object in c:
#             object = ''.join([i for i in object if not i.isdigit()])
            class_names.append(object)
            break
    return class_names

def get_class_index(arg,classes):
    for class_index, c in enumerate(classes):
        if arg in c:
            return class_index #it is like breaking out of the loop
    print("Error:class index not found") #this statement is only executed if class index is not returned.


def empty_directory(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def findsubsets(S,m):
    return set(itertools.combinations(S, m))

def print_table(matrix):
    display(tabulate(matrix, headers='keys', tablefmt='html'))
    
def printmd(string):
    display(Markdown(string))


def save(graphs, domain_name, class_names):
    adjacency_matrix_list = [] # list of adjacency matrices per class
    
    for index, G in enumerate(graphs):
        fig = plt.figure()
        edge_labels=nx.get_edge_attributes(G, 'weight')
        print(edge_labels)
        nx.write_graphml(G, "output/"+ domain_name + "/" +  class_names[index] + ".graphml")
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels = True, connectionstyle='Arc3, rad=0.3')
        nx.draw_networkx_edge_labels(G,pos, edge_labels=edge_labels)
        df = nx.to_pandas_adjacency(G, nodelist=G.nodes(), dtype=int)
        adjacency_matrix_list.append(df)
        #print_table(df)
        fig.savefig("output/"+ domain_name + "/" + class_names[index]+'.png', bbox_inches='tight')
    return adjacency_matrix_list

def plot_cytographs(graphs, domain_name, aml, class_names):
    cytoscapeobs = []
    for index, G in enumerate(graphs):
            cytoscapeobj = CytoscapeWidget()
            cytoscapeobj.graph.add_graph_from_networkx(G)
            edge_list = list()
            for source, target, data in G.edges(data=True):
                edge_instance = Edge()
                edge_instance.data['source'] = source
                edge_instance.data['target'] = target
                for k, v in data.items():
                    cyto_attrs = ['group', 'removed', 'selected', 'selectable',
                        'locked', 'grabbed', 'grabbable', 'classes', 'position', 'data']
                    if k in cyto_attrs:
                        setattr(edge_instance, k, v)
                    else:
                        edge_instance.data[k] = v
                    edge_list.append(edge_instance)
            cytoscapeobj.graph.edges = edge_list
#             cytoscapeobj.graph.add_graph_from_df(aml[index],aml[index].columns.tolist())
            cytoscapeobs.append(cytoscapeobj)
#             print(cytoscapeobj)
            printmd('## class **'+class_names[index]+'**')
            print_table(aml[index])
    #         print("Nodes:{}".format(G.nodes()))
    #         print("Edges:{}".format(G.edges()))
            cytoscapeobj.set_style([{
                            'width':400,
                            'height':400,

                            'selector': 'node',
                            'style': {
                                'label': 'data(id)',
                                'font-family': 'helvetica',
                                'font-size': '8px',
                                'background-color': '#11479e',
                                'height':'10px',
                                'width':'10px',

                                }
                            },
                            {
                            'selector': 'node:parent',
                            'css': {
                                'background-opacity': 0.333,
                                'background-color': '#bbb'
                                }
                            },
                            {
                            'selector': '$node > node',
                            'css': {
                                'padding-top': '10px',
                                'padding-left': '10px',
                                'padding-bottom': '10px',
                                'padding-right': '10px',
                                'text-valign': 'top',
                                'text-halign': 'center',
                                'background-color': '#bbb'
                              }
                            },
                           {
                                'selector': 'edge',

                                'style': {
                                    'label':'data(weight)',
                                    'width': 1,
                                    'line-color': '#9dbaea',
                                    'target-arrow-shape': 'triangle',
                                    'target-arrow-color': '#9dbaea',
                                    'arrow-scale': 0.5,
                                    'curve-style': 'bezier',
                                    'font-family': 'helvetica',
                                    'font-size': '8px',
                                    'text-valign': 'top',
                                    'text-halign':'center'
                                }
                            },
                            ])
            cytoscapeobj.max_zoom = 4.0
            cytoscapeobj.min_zoom = 0.5
            display(cytoscapeobj)
    return cytoscapeobs
def build_and_save_transition_graphs(classes, domain_name, class_names, arguments, sequences):
    # There should be a graph for each class of objects.
    graphs = []
    # Initialize all graphs empty
    for sort in classes:
        graphs.append(nx.DiGraph())

    consecutive_transition_lists = [] #list of consecutive transitions per object instance per sequence.

    for m, arg in enumerate(arguments):  # for all arguments (objects found in sequences)
        for n, seq in enumerate(sequences):  # for all sequences
            consecutive_transition_list = list()  # consecutive transition list for a sequence and an object (arg)
            for i, actarg_tuple in enumerate(seq):
                for j, arg_prime in enumerate(actarg_tuple[1]):  # for all arguments in actarg tuples
                    if arg == arg_prime:  # if argument matches arg
                        node = actarg_tuple[0] + "." +  str(j)
                        # node = actarg_tuple[0] +  "." + class_names[get_class_index(arg,classes)] + "." +  str(j)  # name the node of graph which represents a transition
                        consecutive_transition_list.append(node)  # add node to the cons_transition for sequence and argument

                        # for each class append the nodes to the graph of that class
                        class_index = get_class_index(arg_prime, classes)  # get index of class to which the object belongs to
                        graphs[class_index].add_node(node)  # add node to the graph of that class

            consecutive_transition_lists.append([n, arg, consecutive_transition_list])

    # print(consecutive_transition_lists)
    # for all consecutive transitions add edges to the appropriate graphs.
    for cons_trans_list in consecutive_transition_lists:
        # print(cons_trans_list)
        seq_no = cons_trans_list[0]  # get sequence number
        arg = cons_trans_list[1]  # get argument
        class_index = get_class_index(arg, classes)  # get index of class
        # add directed edges to graph of that class
        for i in range(0, len(cons_trans_list[2]) - 1):
                if graphs[class_index].has_edge(cons_trans_list[2][i], cons_trans_list[2][i + 1]):
                    graphs[class_index][cons_trans_list[2][i]][cons_trans_list[2][i + 1]]['weight'] += 1
                else:
                    graphs[class_index].add_edge(cons_trans_list[2][i], cons_trans_list[2][i + 1], weight=1)


    
    # make directory if doesn't exist
    dirName = "output/"+ domain_name
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        print("Directory ", dirName, " Created ")
    else:
        print("Directory ", dirName, " already exists")
    empty_directory(dirName)
     
    # save all the graphs
    adjacency_matrix_list = save(graphs, domain_name, class_names) # list of adjacency matrices per class

    # plot cytoscape interactive graphs
    cytoscapeobs = plot_cytographs(graphs,domain_name, adjacency_matrix_list, class_names)
    
    return adjacency_matrix_list, graphs, cytoscapeobs



def get_adjacency_matrix_with_holes(adjacency_matrix_list):
    adjacency_matrix_list_with_holes = []
    for index,adjacency_matrix in enumerate(adjacency_matrix_list):
        # print("\n ROWS ===========")
        df = adjacency_matrix.copy()
        df1 = adjacency_matrix.copy()

        # for particular adjacency matrix's copy, loop over all pairs of rows
        for i in range(df.shape[0] - 1):
            for j in range(i+1, df.shape[0]):
                idx1, idx2 = i, j
                row1, row2 = df.iloc[idx1,:], df.iloc[idx2, :] #we have now all pairs of rows

                common_values_flag = False #for each two rows we have a common_values_flag

                # if there is a common value between two rows, turn common value flag to true
                for col in range(row1.shape[0]):
                    if row1.iloc[col] > 0 and row2.iloc[col] > 0:
                        common_values_flag = True
                        break

                # now if two rows have common values, we need to check for holes.
                if common_values_flag:
                    for col in range(row1.shape[0]):
                        if row1.iloc[col] > 0 and row2.iloc[col] == 0:
                            df1.iloc[idx2,col] = 'hole'
                        elif row1.iloc[col] == 0 and row2.iloc[col] > 0:
                            df1.iloc[idx1, col] = 'hole'

        adjacency_matrix_list_with_holes.append(df1)
    return adjacency_matrix_list_with_holes


def get_consecutive_transitions_per_class(adjacency_matrix_list_with_holes):
    consecutive_transitions_per_class = []
    for index, df in enumerate(adjacency_matrix_list_with_holes):
        consecutive_transitions = set()  # for a class
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                if df.iloc[i, j] != 'hole':
                    if df.iloc[i, j] > 0:
#                         print("(" + df.index[i] + "," + df.columns[j] + ")")
                        consecutive_transitions.add((df.index[i], df.columns[j]))
        consecutive_transitions_per_class.append(consecutive_transitions)
    return consecutive_transitions_per_class



def check_well_formed(subset_df):
    # got the adjacency matrix subset
    df = subset_df.copy()
    well_formed_flag = True
    
    
    if (df == 0).all(axis=None): # all elements are zero
        well_formed_flag = False
        
    # for particular adjacency matrix's copy, loop over all pairs of rows
    for i in range(0, df.shape[0]-1):
        for j in range(i + 1, df.shape[0]):
            print(i,j)
            idx1, idx2 = i, j
            row1, row2 = df.iloc[idx1, :], df.iloc[idx2, :]  # we have now all pairs of rows

            common_values_flag = False  # for each two rows we have a common_values_flag

            # if there is a common value between two rows, turn common value flag to true
            for col in range(row1.shape[0]):
                if row1.iloc[col] > 0 and row2.iloc[col] > 0:
                    common_values_flag = True
                    break
          
            if common_values_flag:
                for col in range(row1.shape[0]): # check for holes if common value
                    if row1.iloc[col] > 0 and row2.iloc[col] == 0:
                        well_formed_flag = False
                    elif row1.iloc[col] == 0 and row2.iloc[col] > 0:
                        well_formed_flag = False
    
    if not well_formed_flag:
        return False
    elif well_formed_flag:
        return True

def check_valid(subset_df,consecutive_transitions_per_class):
    
    # Note: Essentially we check validity against P instead of E. 
    # In the paper of LOCM2, it isn't mentioned how to check against E.
    
    # Reasoning: If we check against all consecutive transitions per class, 
    # we essentially check against all example sequences.
    # check the candidate set which is well-formed (subset df against all consecutive transitions)

    # got the adjacency matrix subset
    df = subset_df.copy()

    # for particular adjacency matrix's copy, loop over all pairs of rows
    for i in range(df.shape[0]):
        for j in range(df.shape[0]):
            if df.iloc[i,j] > 0:
                valid_val_flag = False
                ordered_pair = (df.index[i], df.columns[j])
                for ct_list in consecutive_transitions_per_class:
                    for ct in ct_list:
                        if ordered_pair == ct:
                            valid_val_flag=True
                # if after all iteration ordered pair is not found, mark the subset as invalid.
                if not valid_val_flag:
                    return False
                
    # return True if all ordered pairs found.
    return True


def locm2_get_transition_sets_per_class(holes_per_class, transitions_per_class, consecutive_transitions_per_class, class_names, adjacency_matrix_list):
    """LOCM 2 Algorithm in the original LOCM2 paper"""
    
    # contains Solution Set S for each class.
    transition_sets_per_class = []

    # for each hole for a class/sort
    for index, holes in enumerate(holes_per_class):
        class_name = class_names[index]
        printmd("### "+  class_name)
        
        # S
        transition_set_list = [] #transition_sets_of_a_class, # intially it's empty
        
        if len(holes)==0:
            print("no holes") # S will contain just T_all
        
        if len(holes) > 0: # if there are any holes for a class
            print(str(len(holes)) + " holes")
            for ind, hole in enumerate(holes):
                printmd("#### Hole " + str(ind + 1) + ": " + str(set(hole)))
                is_hole_already_covered_flag = False
                if len(transition_set_list)>0:
                    for s_prime in transition_set_list:
                        if hole.issubset(s_prime):
                            printmd("Hole "+ str(set(hole)) + " is already covered.")
                            is_hole_already_covered_flag = True
                            break
                     
                # discover a set which includes hole and is well-formed and valid against test data.
                # if hole is not covered, do BFS with sets of increasing sizes starting with s=hole
                if not is_hole_already_covered_flag: 
                    h = hole.copy()
                    candidate_sets = []
                    # all subsets of T_all starting from hole's len +1 to T_all-1.
                    for i in range(len(h)+1,len(transitions_per_class[index])): 
                        subsets = findsubsets(transitions_per_class[index],i) # all subsets of length i

                        for s in subsets:
                            if h.issubset(s): # if  is subset of s
                                candidate_sets.append(set(s))
                        
                        s_well_formed_and_valid = False
                        for s in candidate_sets:
                            if len(s)>=i:
                                printmd("Checking candidate set *" + str(s) + "* of class **" + class_name + "** for well formedness and Validity")
                                subset_df = adjacency_matrix_list[index].loc[list(s),list(s)]
                                print_table(subset_df)

                                # checking for well-formedness
                                well_formed_flag = False
                                well_formed_flag = check_well_formed(subset_df)
                                if not well_formed_flag:
                                    print("This subset is NOT well-formed")
                                    
                                elif well_formed_flag:
                                    print("This subset is well-formed.")
                                    # if well-formed validate across the data E
                                    # to remove inappropriate dead-ends
                                    valid_against_data_flag = False
                                    valid_against_data_flag = check_valid(subset_df, consecutive_transitions_per_class)
                                    if not valid_against_data_flag:
                                        print("This subset is well-formed but invalid against example data")

                                    if valid_against_data_flag:
                                        print("This subset is valid.")
                                        print("Adding this subset " + str(s) +" to the locm2 transition set.")
                                        if s not in transition_set_list: # do not allow copies.
                                            transition_set_list.append(s)
                                        
                                        print("Hole that is covered now:")
                                        print(list(h))
                                        s_well_formed_and_valid = True
                                        break 
                        if s_well_formed_and_valid:
                                break
                                        
                                        

        print(transition_set_list)                                    
        #step 7 : remove redundant sets S - {s1}
        ts_copy = transition_set_list.copy()
        for i in range(len(ts_copy)):
            for j in range(len(ts_copy)):
                if ts_copy[i] < ts_copy[j]: #if subset
                    if ts_copy[i] in transition_set_list:
                        transition_set_list.remove(ts_copy[i])
                elif ts_copy[i] > ts_copy[j]:
                    if ts_copy[j] in transition_set_list:
                        transition_set_list.remove(ts_copy[j])
        print("\nRemoved redundancy transition set list")
        print(transition_set_list)

        #step-8: include all-transitions machine, even if it is not well-formed.
        transition_set_list.append(set(transitions_per_class[index])) #fallback
        printmd("#### Final transition set list")
        print(transition_set_list)
        transition_sets_per_class.append(transition_set_list)
        

    return transition_sets_per_class


def plot_cytographs_fsm(graph, domain_name):
    cytoscapeobj = CytoscapeWidget()
    cytoscapeobj.graph.add_graph_from_networkx(graph)
    edge_list = list()
    for source, target, data in graph.edges(data=True):
        edge_instance = Edge()
        edge_instance.data['source'] = source
        edge_instance.data['target'] = target
        for k, v in data.items():
            cyto_attrs = ['group', 'removed', 'selected', 'selectable',
                'locked', 'grabbed', 'grabbable', 'classes', 'position', 'data']
            if k in cyto_attrs:
                setattr(edge_instance, k, v)
            else:
                edge_instance.data[k] = v
            edge_list.append(edge_instance)

    cytoscapeobj.graph.edges = edge_list
#     print("Nodes:{}".format(graph.nodes()))
#     print("Edges:{}".format(graph.edges()))
    cytoscapeobj.set_style([{
                    'width':400,
                    'height':500,

                    'selector': 'node',
                    'style': {
                        'label': 'data(id)',
                        'font-family': 'helvetica',
                        'font-size': '8px',
                        'background-color': '#11479e',
                        'height':'10px',
                        'width':'10px',


                        }

                    },
                    {
                    'selector': 'node:parent',
                    'css': {
                        'background-opacity': 0.333,
                        'background-color': '#bbb'
                        }
                    },
                    {
                    'selector': '$node > node',
                    'css': {
                        'padding-top': '10px',
                        'padding-left': '10px',
                        'padding-bottom': '10px',
                        'padding-right': '10px',
                        'text-valign': 'top',
                        'text-halign': 'center',
                        'background-color': '#bbb'
                      }
                    },
                   {
                        'selector': 'edge',

                        'style': {
                            'label':'data(weight)',
                            'width': 1,
                            'line-color': '#9dbaea',
                            'target-arrow-shape': 'triangle',
                            'target-arrow-color': '#9dbaea',
                            'arrow-scale': 0.5,
                            'curve-style': 'bezier',
                            'font-family': 'helvetica',
                            'font-size': '8px',
                            'text-valign': 'top',
                            'text-halign':'center'
                        }
                    },
                    ])
    cytoscapeobj.max_zoom = 2.0
    cytoscapeobj.min_zoom = 0.5
    display(cytoscapeobj)