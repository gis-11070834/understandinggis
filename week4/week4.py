from geopandas import read_file
from sys import exit
from math import sqrt

# set the percentage of nodes that you want to remove
# done in capitals to mark it out --> done for variables defining settings or other definitions that wont be changed when the code runs
# also done as a variable so it is easy to change if we want to change the level of simplification
SIMPLIFICATION_PERC = 98

# imoportant to have these as functions as they will be calld on many times - avoid repetition
def distance(x1, y1, x2, y2):
	return sqrt((x2-x1)**2 + (y2-y1)**2)

# set function to get effective area
def get_effective_area(a, b, c):
	"""
	* Calculate the area of a triangle made from the points a, b and c using Heron's formula
	* 	https://en.wikipedia.org/wiki/Heron%27s_formula
	"""
	# calculate the length of each side
	side_a = distance(b[0], b[1], c[0], c[1])
	side_b = distance(a[0], a[1], c[0], c[1])
	side_c = distance(a[0], a[1], b[0], b[1])

	# calculate semi-perimeter of the triangle (perimeter / 2)
	s = (side_a + side_b + side_c) / 2

	# apply Heron's formula and return
	return sqrt(s * (s - side_a) * (s - side_b) * (s - side_c))

# creating a function of the VW algorithm
# 2 arguments - node_list is the list of points that need to be simplified and n_node is number of nodes returned in the simplified list
def visvalingam_whyatt(node_list, n_nodes):

# open a dataset of all countries in the world
world = read_file("../../data/natural-earth/ne_10m_admin_0_countries.shp")

# extract the UK, project, and extract the geometry
# this line of code is doing 3 things in one line: 
    # filtering the dataset to the UK row, projecting the result to the british national grid, extracting the geometry
uk = world[(world.ISO_A3 == 'GBR')].to_crs("EPSG:27700").geometry.iloc[0]	# COMPLETE THIS LINE

# report geometry type
print(f"geometry type: {uk.geom_type}")

# quit the analysis if we are dealing with any geometry but a MultiPolygon
if uk.geom_type != 'MultiPolygon':
  print("Geometry is not a MultiPolygon, exiting...")
  exit()
  
# initialise variables to hold the coordinates and area of the largest polygon
biggest_area = 0
coord_list = []

# loop through each polygon in the multipolygon and find the biggest (mainland Great Britain)
for poly in uk.geoms:

	# if it is the biggest so far
	if poly.area > biggest_area:	# COMPLETE THIS LINE
    
		# store the new value for biggest area
		biggest_area = poly.area
        
     # store the coordinates of the polygon
		coord_list = list(poly.boundary.coords)	# COMPLETE THIS LINE (look at the variables that you defined before the loop)

# how many nodes do we need?
n_nodes = int(len(coord_list) / 100.0 * (100 - SIMPLIFICATION_PERC))

# ensure that there are at least 3 nodes (minimum for a polygon)
if n_nodes < 3:
	n_nodes = 3 