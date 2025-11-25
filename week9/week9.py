from osmnx import graph_from_xml
from shapely import STRtree
from shapely.geometry import Point
from pyproj import Geod

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
print(ellipsoidal_distance(from_node, to_node))
