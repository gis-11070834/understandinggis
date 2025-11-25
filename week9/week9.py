from osmnx import graph_from_xml
from shapely import STRtree
from shapely.geometry import Point
from pyproj import Geod
from sys import exit
from networkx import NodeNotFound, NetworkXNoPath

def ellipsoidal_distance(node_a, node_b):
	"""
	Calculate the 'as the crow flies' distance between two nodes in a graph using
	 the Inverse Vincenty method, via the PyProj library.
	"""
	# extract the data (the coordinates) from node_a and node_b
	point_a = graph.nodes(data=True)[node_a]
	point_b = graph.nodes(data=True)[node_b] # MISSING LINE

	# compute the distance across the WGS84 ellipsoid (the one used by the dataset)
	return Geod(ellps='WGS84').inv(point_a['x'], point_a['y'], point_b['x'], point_b['y'])[2]

def reconstruct_path(end_node, parent_node, parents):
	"""
	Once we have found the end node of our route, reconstruct the shortest path 
	 to it using the parents list
     
    3 arguments in the function:
        end_node: the end node in the path
        parent_node: the node from which we arrived at the end node
        parents: a dictionary that contains the parent node of each node that we searched
	"""
	# initialise a list that will contain the path, beginning with the current node (the end of the route)
	path = [end_node]
	
	# then get the parent (the node from which we arrived at the end of the route)
	node = parent_node

	# loop back through the list of explored nodes until we reach the start node (the one where parent == None)
	while node is not None:

		# for each node in the path, add it to the path...
		path.append(node)

		# ...and move on to its parent (the one before it in the path)
		node = parents[node]
	
	# finally, reverse the path (so it goes start -> end) and return it
	path.reverse()	# note that this is an 'in place' function that edits the list itself, it does not return anything!
	return path

def astar_path(G, source, target, heuristic):
    """
    Routing algorithm
    """
    #first, make sure that both the `source` and `target` nodes actually exist...
    if source not in G or target not in G:
        raise NodeNotFound(f"Either source ({source}) or target ({target}) is not in the graph")

# create a MultiDiGraph from an XML dataset from OpenStreetMap
graph = graph_from_xml('../../data/kaliningrad/kaliningrad.xml')

# create spatial index from graph
# create point constructor to hold the x & y coordinates of n (1 instead of 0 as 0 position gives index number rather than dictionary point)
idx = STRtree([Point(n[1]['x'], n[1]['y']) for n in graph.nodes(data=True)])
               
# specify the start and end point of your route
from_point = Point(20.483322, 54.692934)
to_point = Point(20.544863, 54.723827)

# calculate the 'from' and 'to' node as the nearest to the specified coordinates
from_node_id, to_node_id = idx.nearest([from_point, to_point])

# get the IDs from the Graph to get the nodes themselves
node_list = list(graph.nodes())
from_node = node_list[from_node_id]
to_node = node_list[to_node_id]

# print the 'from' and 'to' nodes to the console
#print(graph.nodes()[from_node], graph.nodes()[to_node])

# call to test ellipsoidal function
# print(ellipsoidal_distance(from_node, to_node))

# use try statement to catch exceptions
try:
	# calculate the shortest path across the network
	shortest_path = astar_path(graph, 1, 2, ellipsoidal_distance)

# catch exception for no path available
except NodeNotFound:
	print("Sorry, there is no path between those locations in the provided network")
	exit()

# catch exception for no path available
except NetworkXNoPath:
	print("Sorry, there is no path between those locations in the provided network")
	exit()
