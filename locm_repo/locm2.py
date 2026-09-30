'''
| author:
| Shivam Miglani 
| https://github.com/Shivam-Miglani/contextual_drl/blob/master/iLOCM.ipynb
|
| Modified by Serawork WALLELIIGN, LIG lab/ Marven Team, France, 2022.
| Implementation of LOCM2
'''

import os, re
from copy import deepcopy, copy
import networkx as nx
from iLOCM import *

path = "Training sequence/"
fs = os.listdir(path)
print(fs)
files = []

for f in fs:
    if f.endswith(".txt"):
        l = f.split('.')
        files.append(int(l[0]))
for file in sorted(files):
    filename = path + str(file) + ".txt"
    input_sequence=""
    if filename.endswith(".txt"):
        with open(filename) as f:
            lines = f.readlines()
        for line in lines:
            input_sequence+=line
    input_sequence = input_sequence.replace("\n", ",").strip()[:-1]

    sequences = read_input(input_sequence)
    
    print_sequences(sequences)
    domain_name = 'Blocksworld'  # TO-DO extract the name from name given during project creation 
    transitions = set() # A transition is denoted by action_name + argument position
    arguments = set()
    actions = set()
    for seq in sequences:
        for actarg_tuple in seq:
            actions.add(actarg_tuple[0])
            for j, arg in enumerate(actarg_tuple[1]):
                transitions.add(actarg_tuple[0]+"."+str(j))
                arguments.add(arg)
    
    print("\nActions")
    print(actions)
    print("\nArguments/Objects")
    print(arguments)
    
    d = get_actarg_dictionary(sequences)

    classes = get_classes(d) #sorts of object
    print("\nSorts/Classes")
    print(classes)

    class_names = get_class_names(classes)
    print("\nExtracted class names")
    print(class_names)

    # change transitions to be more meaningful by incorporating class_names.
    full_transitions = set()
    for seq in sequences:
        for actarg_tuple in seq:
            actions.add(actarg_tuple[0])
            for j, arg in enumerate(actarg_tuple[1]):
                full_transitions.add(actarg_tuple[0]+"."+class_names[get_class_index(arg,classes)]+'.'+str(j))
                arguments.add(arg)

    print("\nActions")
    print(actions)
    print("\nTransitions")
    print(full_transitions)
    print("\nArguments/Objects")
    print(arguments)

    print("\nNumber of Actions: {},\nNumber of unique transitions: {},\nNumber of unique objects (arguments): {},\nNumber of classes/sorts: {}".format(len(actions), len(transitions), len(arguments), len(classes)))

    #### Build weighted directed graphs for transitions.
    printmd("## "+ domain_name.upper())
    adjacency_matrix_list, graphs, cytoscapeobjs = build_and_save_transition_graphs(classes, domain_name, class_names, arguments, sequences)
    
    adjacency_matrix_list_with_holes = get_adjacency_matrix_with_holes(adjacency_matrix_list)

    # Printing FSM matrices with and without holes
    for index,adjacency_matrix in enumerate(adjacency_matrix_list):
        printmd("\n#### " + class_names[index] )
        print_table(adjacency_matrix)

        printmd("\n#### HOLES: " + class_names[index])
        print_table(adjacency_matrix_list_with_holes[index])

    # Create list of set of holes per class (H)
    holes_per_class = []

    for index,df in enumerate(adjacency_matrix_list_with_holes):
        holes = set()
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                if df.iloc[i,j] == 'hole':
                    holes.add(frozenset({df.index[i] , df.columns[j]}))
        holes_per_class.append(holes)
    for i, hole in enumerate(holes_per_class):
        print("#holes in class " + class_names[i]+":" + str(len(hole)))

    # List of transitions per class (T_all). It is just a set of transitions that occur for a class.
    transitions_per_class = []
    for index, df in enumerate(adjacency_matrix_list_with_holes):
        transitions_per_class.append(df.columns.values)

    #  Create list of consecutive transitions per class (P). If value is not null, ordered pair i,j would be consecutive transitions per class
    consecutive_transitions_per_class = get_consecutive_transitions_per_class(adjacency_matrix_list_with_holes)

    ############    LOCM2 #################
    ####    Input ready for LOCM2, Starting LOCM2 algorithm now
    ####    Step 8:  selecting transition sets (TS) [Main LOCM2 Algorithm]
    printmd("### Getting transitions sets for each class using LOCM2")
    transition_sets_per_class = locm2_get_transition_sets_per_class(holes_per_class, transitions_per_class, consecutive_transitions_per_class, class_names, adjacency_matrix_list)

    state_machines_overall_list = []

    for index, ts_class in enumerate(transition_sets_per_class):
        fsms_per_class = []
        printmd("### "+ class_names[index])
        num_fsms = len(ts_class)
        print("Number of FSMS:" + str(num_fsms))
        
        for fsm_no, ts in enumerate(ts_class):
            fsm_graph = nx.DiGraph()
            
            printmd("#### FSM " + str(fsm_no))
            for t in ts:
                source = "s(" + str(t) + ")"
                target = "e(" + str(t) + ")"
                fsm_graph.add_edge(source,target,weight=t)
            
           
            t_df = adjacency_matrix_list[index].loc[list(ts), list(ts)] #transition df for this fsm
            #print_table(t_df)
            
            
            # merge end(t1) = start(t2) from transition df
            
            edge_t_list = [] # edge transition list
            for i in range(t_df.shape[0]):
                for j in range(t_df.shape[1]):
                    
                    if t_df.iloc[i, j] != 'hole':
                        if t_df.iloc[i, j] > 0:
                            for node in fsm_graph.nodes():
                                if "e("+t_df.index[i]+")" in node:
                                    merge_node1 = node
                                if "s("+t_df.index[j]+")" in node:
                                    merge_node2 = node
                            
                            
                            

                            fsm_graph = nx.contracted_nodes(fsm_graph, merge_node1, merge_node2 , self_loops=True)

                            if merge_node1 != merge_node2:
                                mapping = {merge_node1: merge_node1 + "|" + merge_node2} 
                                fsm_graph = nx.relabel_nodes(fsm_graph, mapping)

            # we need to complete the list of transitions 
            # that can happen on self-loop nodes 
            # as these have been overwritten (as graph is not MultiDiGraph)
            
            sl_state_list = list(nx.nodes_with_selfloops(fsm_graph)) # self looping states.
            # if state is self-looping
            t_list = []
            if len(sl_state_list)>0: 
                # if s(T1) and e(T1) are there for same node, this T1 can self-loop occur.
                for s in sl_state_list:
                    for sub_s in s.split('|'):
                        if sub_s[0] == 'e':
                            if ('s' + sub_s[1:]) in s.split('|'):
                                t_list.append(sub_s[2:-1])
                    fsm_graph[s][s]['weight'] = '|'.join(t_list)
            
            

                   
            plot_cytographs_fsm(fsm_graph,domain_name)
            df = nx.to_pandas_adjacency(fsm_graph, nodelist=fsm_graph.nodes(), weight = 1)
            print_table(df)
            fsms_per_class.append(fsm_graph)
        state_machines_overall_list.append(fsms_per_class)


    # An Automatic state dictionary is added here where states are 
    # renamed as 0, 1, 2 etc. for a specific FSM

    state_mappings_class = []
    state_machines_overall_list_2 = []
    for index, fsm_graphs in enumerate(state_machines_overall_list):
        state_mappings_fsm = []
        fsms_per_class_2 = []
        printmd("### "+ class_names[index])
        num_fsms = len(fsm_graphs)
        print("Number of FSMS:" + str(num_fsms))
        
        for fsm_no, G in enumerate(fsm_graphs):
            
            state_mapping = {k: v for v, k in enumerate(G.nodes())}
            G_copy = nx.relabel_nodes(G, state_mapping)
            
            plot_cytographs_fsm(G, domain_name)
            plot_cytographs_fsm(G_copy, domain_name)
            printmd("Fsm "+ str(fsm_no))
            fsms_per_class_2.append(G_copy)
            state_mappings_fsm.append(state_mapping)
            
        state_machines_overall_list_2.append(fsms_per_class_2)
        state_mappings_class.append(state_mappings_fsm)


    HS_list = []
    ct_list = []

    # for transition set of each class
    for index, ts_class in enumerate(transition_sets_per_class):
        printmd("### "+ class_names[index])
        
        ct_per_class = []
        HS_per_class = []
        
        # for transition set of each fsm in a class
        for fsm_no, ts in enumerate(ts_class):
            printmd("#### FSM: " + str(fsm_no) + " Hypothesis Set")
            
            # transition matrix for the ts
            t_df = adjacency_matrix_list[index].loc[list(ts), list(ts)]
            ct_in_fsm = set()  # find consecutive transition set for a state machine in a class.
            for i in range(t_df.shape[0]):
                for j in range(t_df.shape[1]):
                    if t_df.iloc[i, j] != 'hole':
                        if t_df.iloc[i, j] > 0:
                            ct_in_fsm.add((t_df.index[i], t_df.columns[j]))
            
            ct_per_class.append(ct_in_fsm)
            
            # add to hypothesis set
            HS = set()
            
            # for each pair B.k and C.l in TS s.t. e(B.k) = S = s(C.l)
            for ct in ct_in_fsm:
                B = ct[0].split('.')[0] # action name of T1
                k = int(ct[0].split('.')[1]) # argument index of T1
                
                C = ct[1].split('.')[0] # action name of T2
                l = int(ct[1].split('.')[1]) # argument index of T2
                
                # When both actions B and C contain another argument of the same sort G' in position k' and l' respectively, 
                # we hypothesise that there may be a relation between sorts G and G'.
                for seq in sequences:
                    for actarg_tuple in seq:
                        arglist1 = []
                        arglist2 = []
                        if actarg_tuple[0] == B: #if action name is same as B
                            arglist1 = actarg_tuple[1].copy()
    #                         arglist1.remove(actarg_tuple[1][k]) # remove k from arglist
                            for actarg_tuple_prime in seq: #loop through seq again.
                                if actarg_tuple_prime[0] == C:
                                    arglist2 = actarg_tuple_prime[1].copy()
    #                                 arglist2.remove(actarg_tuple_prime[1][l]) # remove l from arglist
                                    

                            # for arg lists of actions B and C, if class is same add a hypothesis set.
                            for i in range(len(arglist1)): # if len is 0, we don't go in
                                for j in range(len(arglist2)):
                                    class1 = get_class_index(arglist1[i], classes)
                                    class2 = get_class_index(arglist2[j], classes)
                                    if class1 == class2: # if object at same position have same classes
                                        # add hypothesis to hypothesis set.
                                        if (k!=i) and (l!=j):
                                            HS.add((frozenset({"e("+B+"."+ str(k)+")", "s("+C+"."+str(l)+")"}),B,k,i,C,l,j,class_names[index],class_names[class1]))
            print(str(len(HS))+ " hypothesis created")
    #         for h in HS:
    #             print(h)
            
            HS_per_class.append(HS)
        HS_list.append(HS_per_class)
        ct_list.append(ct_per_class)


    HS_list_retained = []
    for index, HS_class in enumerate(HS_list):
        printmd("### "+ class_names[index])
        HS_per_class_retained = []


        for fsm_no, HS in enumerate(HS_class):
            printmd("#### FSM: " + str(fsm_no) + " Hypothesis Set")

            count=0
            HS_copy = HS.copy()
            HS_copy2 = HS.copy()

            
            # for each object O occuring in Ou
            for O in arguments:
                #   for each pair of transitions Ap.m and Aq.n consecutive for O in seq
                ct = []
                for seq in sequences:
                    for actarg_tuple in seq:
                        act = actarg_tuple[0]
                        for j, arg in enumerate(actarg_tuple[1]):
                            if arg == O:
                                ct.append((act + '.' + str(j), actarg_tuple[1]))


                for i in range(len(ct)-1):
                    A_p = ct[i][0].split('.')[0]
                    m = int(ct[i][0].split('.')[1])
                    A_q = ct[i+1][0].split('.')[0]
                    n = int(ct[i+1][0].split('.')[1]) 

                    # for each hypothesis H s.t. A_p = B, m = k, A_q = C, n = l

                    for H in HS_copy2:
                        if A_p == H[1] and m == H[2] and A_q == H[4] and n == H[5]:
                            k_prime = H[3]
                            l_prime = H[6]

                            # if O_p,k_prime = Q_q,l_prime
                            if ct[i][1][k_prime] != ct[i+1][1][l_prime]:
                                if H in HS_copy:
                                    HS_copy.remove(H)
                                    count += 1

            print(str(len(HS_copy))+ " hypothesis retained")
            # state machine
    #         if len(HS_copy)>0:
    #             plot_cytographs_fsm(state_machines_overall_list[index][fsm_no],domain_name)
    #         for H in HS_copy:
    #             print(H)
            HS_per_class_retained.append(HS_copy)
        HS_list_retained.append(HS_per_class_retained)


    # Each hypothesis refers to an incoming and outgoing transition 
    # through a particular state of an FSM
    # and matching associated transitions can be considered
    # to set and read parameters of a state.
    # Since there maybe multiple transitions through a give state,
    # it is possible for the same parameter to have multiple
    # pairwise occurences.

    print("Step 6: creating and merging state params")
    param_bindings_list_overall = []
    for classindex, HS_per_class in enumerate(HS_list_retained):
        param_bind_per_class = []
        
        
        for fsm_no, HS_per_fsm in enumerate(HS_per_class):
            param_binding_list = []
            
            # fsm in consideration
            G = state_machines_overall_list[classindex][fsm_no]
            state_list = G.nodes()
            
            # creation
            for index,h in enumerate(HS_per_fsm):
                param_binding_list.append((h,"v"+str(index)))
            
            merge_pl = [] # parameter to merge list
            if len(param_binding_list)>1:
                # merging
                pairs = findsubsets(param_binding_list, 2)
                for pair in pairs:
                    h_1 = pair[0][0]
                    h_2 = pair[1][0]
                    
                    
                    # equate states
                    state_eq_flag = False
                    for s_index, state in enumerate(state_list):
                        # if both hyp states appear in single state in fsm
                        if list(h_1[0])[0] in state:
                            if list(h_1[0])[0] in state:
                                state_eq_flag =True
                                
                    
                    if ((state_eq_flag and h_1[1] == h_2[1] and h_1[2] == h_2[2] and h_1[3] == h_2[3]) or (state_eq_flag and h_1[4] == h_2[4] and h_1[5] == h_2[5] and h_1[6] == h_2[6])):
                        merge_pl.append(list([pair[0][1], pair[1][1]]))

                        #inner lists to sets (to list of sets)
            l=[set(x) for x in merge_pl]

            #cartesian product merging elements if some element in common
            for a,b in itertools.product(l,l):
                if a.intersection( b ):
                    a.update(b)
                    b.update(a)

            #back to list of lists
            l = sorted( [sorted(list(x)) for x in l])

            #remove dups
            merge_pl = list(l for l,_ in itertools.groupby(l))
            
            # sort
            for pos, l in enumerate(merge_pl):
                merge_pl[pos] = sorted(l, key = lambda x: int(x[1:]))
            
            print(merge_pl) # equal params appear in a list in this list.
              
                
            for z,pb in enumerate(param_binding_list):
                for l in merge_pl:
                    if pb[1] in l:
                        # update pb
                        param_binding_list[z] = (param_binding_list[z][0], l[0])
            

                    
            
            param_bind_per_class.append(param_binding_list)
            print(class_names[classindex])
            
            # set of params per class
            param = set()
            for pb in param_binding_list:
    #             print(pb)
                param.add(pb[1])
                
            # num of params per class
            printmd("No. of params earlier:" + str(len(param_binding_list)))
            printmd("No. of params after merging:" + str(len(param)))
                
            
            
            
            
        param_bindings_list_overall.append(param_bind_per_class)

    # Removing State Params.
    # Flaw occurs Object can reach state S with param P having an inderminate value.
    # There is transition s.t. end(B.k) = S. 
    # but there is no h = <S,B,k,k',C,l,l',G,G') and <h,P> is in bindings.

    para_bind_overall_fault_removed  = []
    for classindex, fsm_per_class in enumerate(state_machines_overall_list):
        print(class_names[classindex])
        pb_per_class_fault_removed = []

        for fsm_no, G in enumerate(fsm_per_class):
            
            pb_per_fsm_fault_removed = []
            # G is fsm in consideration
            faulty_pb = []
            for state in G.nodes():
                inedges = G.in_edges(state, data=True)
                
                for ie in inedges:
                    tr = ie[2]['weight']
                    t_list = tr.split('|')
                    for t in t_list:
                        B = t.split('.')[0]
                        k = t.split('.')[1]
                        S = 'e(' + t + ')'
                        flaw = True
                        for pb in param_bindings_list_overall[classindex][fsm_no]:
                            H = pb[0]
                            v = pb[1]
                            if (S in set(H[0])) and (B==H[1]) and (int(k)==H[2]) :
                                # this pb is okay
                                flaw=False
    #                     print(flaw)
                        if flaw:
                            for pb in param_bindings_list_overall[classindex][fsm_no]:
                                H = pb[0]
                                H_states = list(H[0])
                                for h_state in H_states:
                                    if h_state in state:
                                        if pb not in faulty_pb:
                                            faulty_pb.append(pb) # no duplicates
            
            for pb in param_bindings_list_overall[classindex][fsm_no]:
                if pb not in faulty_pb:
                    pb_per_fsm_fault_removed.append(pb)
            
                                    
                            
                            
            print(str(len(pb_per_fsm_fault_removed)) + "/" + str(len(param_bindings_list_overall[classindex][fsm_no])) + " param retained")
            for pb in pb_per_fsm_fault_removed:
                print(pb)

            pb_per_class_fault_removed.append(pb_per_fsm_fault_removed)
        para_bind_overall_fault_removed.append(pb_per_class_fault_removed)


    # get action schema
    #print(";;********************Learned PDDL domain******************")
    output_file = "output/"+ domain_name + "/" + domain_name + ".pddl"
    write_file = open(output_file, 'w')
    write_line = "(define"
    write_line += "  (domain "+ domain_name+")\n"
    write_line += "  (:requirements :typing)\n"
    write_line += "  (:types"
    for class_name in class_names:
        write_line += " " + class_name
    write_line += ")\n"
    write_line += "  (:predicates\n"

    # one predicate to represent each object state

    predicates = []
    for class_index, pb_per_class in enumerate(para_bind_overall_fault_removed):
        for fsm_no, pbs_per_fsm in enumerate(pb_per_class):
            for state_index, state in enumerate(state_machines_overall_list[class_index][fsm_no].nodes()):
                
                state_set = set(state.split('|'))
                predicate = ""
           
                write_line += "    (" + class_names[class_index] + "_fsm" + str(fsm_no) + "_" +  state
                predicate += "    (" + class_names[class_index] + "_fsm" + str(fsm_no) + "_" + state
                for pb in pbs_per_fsm:
                        if set(pb[0][0]) <= state_set:
                            if " ?"+pb[1] + " - " + str(pb[0][8]) not in predicate:
                                write_line += " ?"+pb[1] + " - " + str(pb[0][8])
                                predicate += " ?"+pb[1] + " - " + str(pb[0][8])
        
                write_line += ")\n"
                predicate += ")"
                predicates.append(predicate)
    write_line += "  )\n"
                
    for action_index, action in enumerate(actions):
        write_line += "\n"
        write_line += "  (:action"
        write_line += "  " + action + " "
        write_line += "  :parameters"
        write_line += "  ("
        arg_already_written_flag = False
        params_per_action = []
        args_per_action = []
        for seq in sequences:
            for actarg_tuple in seq:
                if not arg_already_written_flag:
                    if actarg_tuple[0] == action:
                        arglist = []
                        for arg in actarg_tuple[1]:
                            write_line += "?"+arg + " - " + class_names[get_class_index(arg,classes)] + " "
                            arglist.append(arg)
                        args_per_action.append(arglist)
                        params_per_action.append(actarg_tuple[1])
                        arg_already_written_flag = True

        write_line += ")\n"


        # need to use FSMS to get preconditions and effects.
        # Start-state = precondition. End state= Effect
        preconditions = []
        effects = []
        for arglist in params_per_action:
            for arg in arglist:
                current_class_index = get_class_index(arg, classes)
                for fsm_no, G in enumerate(state_machines_overall_list[current_class_index]):
    #                
                    for start, end, weight in G.edges(data='weight'):
                        _actions = weight.split('|')
                        for _action in _actions:
                            
                            if _action.split('.')[0] == action:
                                for predicate in predicates:
                                    pred = predicate.split()[0].lstrip("(")
                                    clss = pred.split('_')[0]
                                    fsm = pred.split('_')[1]
                                    state = set(pred.split('_')[2].replace('))',')').split('|'))



                                    if clss == class_names[current_class_index]:
                                        if fsm == "fsm" + str(fsm_no):

                                            if state == set(start.split('|')):

                                                if predicate not in preconditions:
                                                    preconditions.append(predicate)

                                            if state == set(end.split('|')):
                                                if predicate not in effects:
                                                    effects.append(predicate)
                                break
                                            
        
                    

        write_line += "   :precondition"
        write_line += "   (and\n"
        for precondition in preconditions:
            # precondition = precondition.replace(?)
            write_line += "    "+precondition+"\n"
        write_line += "   )\n"
        write_line += "   :effect"
        write_line += "   (and\n"
        for effect in effects:
            write_line += "    " + effect + "\n"
        write_line += "  )"
        write_line += ")\n"

        write_line += ")\n" #domain ending bracket


    print(write_line)

    write_file.write(write_line)
    write_file.close()
    
    # get action schema
    #print(";;********************Learned PDDL domain******************")
    output_file = "output/"+ domain_name + "/" +  domain_name + ".pddl"
    write_file = open(output_file, 'w')
    write_line = "(define"
    write_line += "  (domain "+ domain_name+")\n"
    write_line += "  (:requirements :typing)\n"
    write_line += "  (:types"
    for class_name in class_names:
        write_line += " " + class_name
    write_line += ")\n"
    write_line += "  (:predicates\n"

    # one predicate to represent each object state

    predicates = []
    for class_index, pb_per_class in enumerate(para_bind_overall_fault_removed):
        for fsm_no, pbs_per_fsm in enumerate(pb_per_class):
            state_mapping = state_mappings_class[class_index][fsm_no]
            
            for state_index, state in enumerate(state_machines_overall_list[class_index][fsm_no].nodes()):
                
                state_set = set(state.split('|'))
                predicate = ""
           
                write_line += "    (" + class_names[class_index] + "_fsm" + str(fsm_no) + "_state" +  str(state_mapping[state])
                predicate += "    (" + class_names[class_index] + "_fsm" + str(fsm_no) + "_state" + str(state_mapping[state])
                for pb in pbs_per_fsm:
                        if set(pb[0][0]) <= state_set:
                            if " ?"+pb[1] + " - " + str(pb[0][8]) not in predicate:
                                write_line += " ?"+pb[1] + " - " + str(pb[0][8])
                                predicate += " ?"+pb[1] + " - " + str(pb[0][8])
        
                write_line += ")\n"
                predicate += ")"
                predicates.append(predicate)
    write_line += "  )\n"
                
    for action_index, action in enumerate(actions):
        write_line += "  (:action"
        write_line += "  " + action + " "
        write_line += "  :parameters"
        write_line += "  ("
        arg_already_written_flag = False
        params_per_action = []
        args_per_action = []
        for seq in sequences:
            for actarg_tuple in seq:
                if not arg_already_written_flag:
                    if actarg_tuple[0] == action:
                        arglist = []
                        for arg in actarg_tuple[1]:
                            write_line += "?"+arg + " - " + class_names[get_class_index(arg,classes)] + " "
                            arglist.append(arg)
                        args_per_action.append(arglist)
                        params_per_action.append(actarg_tuple[1])
                        arg_already_written_flag = True
        write_line += ")\n"


        # need to use FSMS to get preconditions and effects.
        # Start-state = precondition. End state= Effect
        preconditions = []
        effects = []
        for arglist in params_per_action:
            for arg in arglist:
                current_class_index = get_class_index(arg, classes)
                for fsm_no, G in enumerate(state_machines_overall_list[current_class_index]):
                    G_int = state_machines_overall_list_2[current_class_index][fsm_no]
                    state_mapping = state_mappings_class[current_class_index][fsm_no]
                    for start, end, weight in G_int.edges(data='weight'):
                        _actions = weight.split('|')
                        for _action in _actions:
                            if _action.split('.')[0] == action:
                                for predicate in predicates:
                                    pred = predicate.split()[0].lstrip("(")
                                    clss = pred.split('_')[0]
                                    fsm = pred.split('_')[1]
                                    state_ind = pred.split('_')[2].rstrip(")")[-1]

                                    if clss == class_names[current_class_index]:
                                        if fsm == "fsm" + str(fsm_no):
                                            if int(state_ind) == int(start):
                                                if predicate not in preconditions:
                                                    preconditions.append(predicate)
                                                    
                                            if int(state_ind) == int(end):
                                                if predicate not in effects:
                                                    effects.append(predicate)
                                break
                                

                    

        write_line += "   :precondition"
        write_line += "   (and\n"
        for precondition in preconditions:
            write_line += "    "+precondition+"\n"
        write_line += "   )\n"
        write_line += "   :effect"
        write_line += "   (and\n"
        for effect in effects:
            write_line += "    " + effect + "\n"
        write_line += "  )"

        write_line += ")\n\n"

    write_line += ")\n" #domain ending bracket
    print(write_line)

    write_file.write(write_line)
    write_file.close()


    dic = {}
    print(state_mappings_class)
    print(class_names)
    for index, sm_fsm in enumerate(state_mappings_class):
        print("## Class " + str(index))
        print("### "+ class_names[index])

        
        for fsm_no, mapping in enumerate(sm_fsm):
            print("Fsm "+ str(fsm_no))
            print(mapping)


    f = open("output/"+ domain_name + "/" + "dict.txt","w")
    f.write( str(state_mappings_class) )
    f.write("\n" + "Class names")
    f.write(str(class_names))
    f.close()
