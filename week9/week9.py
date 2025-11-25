from osmnx import graph_from_xml
from shapely import STRtree
from shapely.geometry import Point
from pyproj import Geod
from sys import exit
from networkx import NodeNotFound, NetworkXNoPath
from heapq import heappush, heappop

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
        for neighbour in distances:

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
        
        print(estimated_dist)
        exit
                
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

# catch exception for no path available
except NodeNotFound:
    print("Sorry, there is no path between those locations in the provided network")
    exit()

# catch exception for no path available
except NetworkXNoPath:
    print("Sorry, there is no path between those locations in the provided network")
    exit()
