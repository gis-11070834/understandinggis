from geopandas import read_file
from sys import exit

# set the percentage of nodes that you want to remove
# done in capitals to mark it out --> done for variables defining settings or other definitions that wont be changed when the code runs
# also done as a variable so it is easy to change if we want to change the level of simplification
SIMPLIFICATION_PERC = 98

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