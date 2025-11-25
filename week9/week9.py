from osmnx import graph_from_xml
from shapely import STRtree
from shapely.geometry import Point
from pyproj import Geod
from sys import exit
from networkx import NodeNotFound, NetworkXNoPath
from heapq import heappush, heappop
from shapely.geometry import LineString
from geopandas import GeoSeries
from geopandas import read_file
from shapely.geometry import Point
from matplotlib.patches import Patch
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.pyplot import subplots, savefig, Line2D

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
    path.reverse()    # note that this is an 'in place' function that edits the list itself, it does not return anything!
    return path

def astar_path(G, source, target, heuristic):
    """
    Routing algorithm
    """
    #first, make sure that both the `source` and `target` nodes actually exist...
    if source not in G or target not in G:
        raise NodeNotFound(f"Either source ({source}) or target ({target}) is not in the graph")
    
    # create a counter to prevent to ensure that each item in the heap queue will have a unique value (as two could theoretically have the same estimated distance)
    counter = 0

    # initialise a list for the heap queue. This will be a list of tuples, each containing 4 values:
    # `priority`: this is the value on which the list will be sorted by the heap queue algorithm. In 
    #      our case, this will be the estimated distance for this node (the network distance from the
    #      start to this node + the straight line distance from this node to the end) 
    # `counter`: this is simply a unique number to make sure that the algorithm can sort nodes with 
    #      equal `priority` values
    # `node`: the ID of the node to which this entry refers 
    # `cost`: this is the network distance between the start point and the node, used as part of our
    #      routing algorithm (storing it prevents us from needing to calculate the same distance multiple 
    #      times)
    # `parent`: the ID of the node immediately before this one in the path
    queue = [(0, counter, source, 0, None)]

    # dictionary to keep track of the network distance from the start to this node, and the straight
    #     line distance from this node to the end point. This is used to decide which is the best parent 
    #     for each node that we record in the `parents`` dictionary
    distances = {}

    # dictionary to keep track of the parent of each node that we have explored. This is used when we 
    #     come to reconstruct the route once we reach the end point
    parents = {}
    
    # keep going as long as there are more nodes to search
    while queue:

        # pop the next node, its network distance from the start, and its parent from the queue
        cur_node, cur_net_dist, cur_parent = heappop(queue)[2:]    # use list slicing to ignore the first two items
        
        ''' Section 1: a series of checks for whether we should reject the node ''' 

        # check if we have reached the destination
        if cur_node == target:

            # if so, reconstruct the path and return
            return reconstruct_path(cur_node, cur_parent, parents)
        
        ''' Section 2: if we are visiting a node we have already seen '''

        # check if we have already explored this node
        if cur_node in parents:

            # if we are back at the start, abandon this path and try the next one
            if parents[cur_node] is None:
                continue
                
            # if we already have a shorter path to this node, abandon this new path and try the next one
            if distances[cur_node][0] < cur_net_dist:
                continue
        
        ''' Section 3: Assessing the node to be part of the shortest path '''
        
        # add the parent of the current node to the list of parents
        parents[cur_node] = cur_parent

        # get the neighbours for the current node (under assessment)
        for neighbour, edge_data in G[cur_node].items():

            # work out the network distance to this neighbour from the start of the path - this
            #     is simply the distance to the current node (which we already know), plus the 
            #     distance from that node to this neighbour (which is stored in the edge data)
            dist_from_start = cur_net_dist + edge_data[0]['length']
        
            ''' Section 4: Seeing if we have already seen this neighbour '''
      
            # have we already seen this neighbour?
            if neighbour in distances:

                # as we have been get the network distance from the start via the previous and straight 
                #  line distance to the end
                previous_dist_from_start, dist_to_end = distances[neighbour]

                # if the previous path we found to this node is shorter, abandon this new path
                if previous_dist_from_start <= dist_from_start:
                    continue
                
            # if we haven't seen this neighbour before, calculate the straight line distance to the end
            else:
                dist_to_end = heuristic(neighbour, target)
        
            ''' Section 5: Calculate the estimated distance for the route through that node '''
        
            # add the two distances to the distances dictionary
            distances[neighbour] = (dist_from_start, dist_to_end)

            # work out the estimated distance for this path (the network distance from the start to 
            #  this node + the straight line distance from this node to the end). This will act as the 
            #  priority value for our heap queue - the route with the shortest estimated didstance will 
            #  be assessed first.
            estimated_dist = dist_from_start + dist_to_end
        
            ''' Section 6: Adding this node to the heap queue for future assessment in next while loop iteration'''
        
            # increment counter and push to heap
            counter += 1
            heappush(queue, (estimated_dist, counter, neighbour, dist_from_start, cur_node))

    # if the loop finishes, we didn't find a route - raise an exception
    raise NetworkXNoPath(f"Node {target} not reachable from {source}")

def path_to_linestring(start_point, path_list, end_point):
	"""
	Convert a shortest path to a LineString object
	"""
	# initialise the list with the start point
	line = [start_point]

	# loop through each node in the shortest path and load into list
	for n in path_list:

		# get the relevant node from the graph with lat lng data
		node = graph.nodes(data=True)[n]

		# load the lat lng data into the lineString
		line.append(Point(node['x'], node['y']))  ## MISSING LINE (see your spatial index for how to get coordinates from nodes...)

	# append end point to list
	line.append(end_point)

	# store as a LineString
	return LineString(line)

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
    shortest_path = astar_path(graph, from_node, to_node, ellipsoidal_distance)

    #print(shortest_path)
    
    # convert linestring to GeoSeries and project to UTM zone 34
    wgs84 = "+proj=utm +zone=34 +datum=WGS84 +units=m +no_defs +type=crs"
    utm34 = "+proj=utm +zone=34 +datum=WGS84 +units=m +no_defs +type=crs"
    path = GeoSeries(path_to_linestring(from_point, shortest_path, to_point), crs=wgs84).to_crs(utm34)
    
    #print(path)
    
# catch exception for no path available
except NodeNotFound:
    print("Sorry, there is no path between those locations in the provided network")
    exit()

# catch exception for no path available
except NetworkXNoPath:
    print("Sorry, there is no path between those locations in the provided network")
    exit()

# open buildings and water shapefiles
buildings = read_file('../../data/kaliningrad/buildings.shp').to_crs(utm34)
water = read_file('../../data/kaliningrad/water.shp').to_crs(utm34)

# create map axis object, remove axes, set title
fig, my_ax = subplots(1, 1, figsize=(16, 10))
my_ax.axis('off')
my_ax.set(title="The 4 Bridges of Kaliningrad")

# set bounds
buffer = 1000
my_ax.set_xlim([path.geometry.iloc[0].bounds[0] - buffer, path.geometry.iloc[0].bounds[2] + buffer])
my_ax.set_ylim([path.geometry.iloc[0].bounds[1] - buffer, path.geometry.iloc[0].bounds[3] + buffer])

# add the water
water.plot(
	ax=my_ax,
	color='#a6cee3',
	linewidth = 1,
	zorder=1)

# add the buildings
buildings.plot(
	ax=my_ax,
	color='grey',
	linewidth = 1,
	zorder=2)

# add the path
path.plot(
	ax=my_ax,
	color='#984ea3',
	linewidth = 3,
	zorder=4)

# add the start point
GeoSeries(Point(from_point), crs=wgs84).to_crs(utm34).plot(
  ax = my_ax,
  markersize = 60,
  color = 'blue',
  edgecolor = 'black',
  zorder=5)

# add the end point
GeoSeries(Point(to_point), crs=wgs84).to_crs(utm34).plot(
  ax = my_ax,
  markersize = 60,
  color = 'red',
  edgecolor = 'black',
	zorder=6)

# manually draw a legend
my_ax.legend([
	Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markeredgecolor='black', markersize=8),
	Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='black', markersize=8),
    Patch(facecolor='grey'),
    Patch(facecolor='#a6cee3', edgecolor='#a6cee3'),
	Line2D([0], [0], color='#984ea3', lw=3),
	Line2D([0], [0], color='#4daf4a', lw=3)],
	['Origin', 'Destination', 'Buildings', 'Water', 'Path', 'Path(NX)'], loc='lower right')

# add north arrow
x, y, arrow_length = 0.99, 0.99, 0.1
my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
	arrowprops=dict(facecolor='black', width=5, headwidth=15),
	ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)

# add scalebar
my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower left"))

# save the result
savefig(f'./out/10.png', bbox_inches='tight')
print("done!")

