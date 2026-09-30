import os
import sys
import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt

class PlotGraph:
	def __init__(self, path):
		self.path = path

	def plot_graph(self):
		G = nx.read_graphml(self.path)

		print(nx.info(G))
		nx.draw(G, with_labels = True)
		#f = plt
		return plt
"""
path= "/home/sera/Documents/LOCM/output/2-puzzle/"
topo_str = 'Position.graphml'

pg = PlotGraph(path+topo_str)
f = pg.plot_graph()
f.savefig(topo_str.split('.')[0]+'.png', bbox_inches='tight')
"""