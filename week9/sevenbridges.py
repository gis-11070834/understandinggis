# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 11:47:09 2025

@author: k67630sc
"""

from networkx import MultiGraph

# Create a graph object
graph = MultiGraph()

# Add the 4 islands (nodes), colours as per the above diagram
graph.add_node('Blue')
graph.add_node('Green')
graph.add_node('Yellow')
graph.add_node('Orange')

# Add the 7 bridges (edges), colours as per the above diagram
graph.add_edge('Blue','Green', id=1) # e.g. this is a bridge from the Blue to Green island
graph.add_edge('Blue','Orange', id=2)	
graph.add_edge('Blue','Yellow', id=3)
graph.add_edge('Green','Blue', id=4)
graph.add_edge('Green','Orange', id=5)
graph.add_edge('Orange', 'Yellow', id=6)
graph.add_edge('Yellow','Blue', id=7)

# Print a report about the graph that you have just made
print(f"We have {len(list(graph.edges()))} bridges between {len(list(graph.nodes()))} islands.")