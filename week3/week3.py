# THIS IMPORTS A SQUARE ROOT FUNCTION, WHICH IS A BIG HINT!!
from math import sqrt

def distance(x1, y1, x2, y2):
	"""
	* Use Pythagoras' theorem to measure the distance. This is acceptable in this case because:
	*	 - the CRS of the data is a local projection
	*	 - the distances are short
	*  - computational efficiency is important (as we are making many measurements)
	"""
	return sqrt((x2-x1)**2 + (y2-y1)**2)

result = distance (345678, 456789, 445678, 556789)
print(result)

from geopandas import read_file
from shapely import STRtree

# read in shapefiles, ensure that they all have the same CRS
pop_points = read_file("../../data/gulu/pop_points.shp")
water_points = read_file("../../data/gulu/water_points.shp")
gulu_district = read_file("../../data/gulu/district.shp")

# read in the `water_points` dataset AND transform it the the same CRS as `pop_points`
water_points = read_file("../../data/gulu/water_points.shp").to_crs(pop_points.crs)

print(pop_points.crs.to_epsg())
print(water_points.crs.to_epsg())
print(gulu_district.crs.to_epsg())

print(f"population points: {len(pop_points.index)}")
print(f"Initial wells: {len(water_points.index)}")

# get the geometries from the water points geodataframe as a list - using .geometry to get the geometry colum from the waterpoints dataset
# the .tolist() function converts it from a pandas.series object to a list
geoms = water_points.geometry.to_list()

# initialise an instance of an STRtree using the geometries - store in idx variable creating a tree of the geometry
# loads the list into a STRtree() object --> the STRtree constructor then calculates the bounding box for each geometry and loads it into the RTree spatial index
idx = STRtree(geoms)

#1. retrive the polygon geometry using the .iloc[0] (get the dataset at index location 0 - only row in table) and reoprt the number of boreholes in the dataset using a print() statement and f-string
# get the one and only polygon from the district dataset
polygon = gulu_district.geometry.iloc[0]

# how many rows are we starting with?
print(f"Initial wells: {len(water_points.index)}")

#2. use the .query() function of your STRtree object to return a list of borehold IDs that intersect the district polygon
# get the indexes of wells that intersect bounds of the district
possible_matches_index = idx.query(polygon)

#3. use the resulting list to query the water_points GDF using .iloc
# this time we are passing a list of index numbers to it, rather than just a single one as in step 1
# report the number of boreholes that meet this critera
# use those indexes to extract the possible matches from the GeoDataFrame
possible_matches = water_points.iloc[possible_matches_index]

# how many rows are left now? 
# we use index (list of ID numbers that correspond to each row) normally as its guaranteed in every dataset
print(f"Filtered wells: {len(possible_matches.index)}")

#4. use the smaller data set to do the precise (but slower) within query which gives Boolean values back (true, false) for whether its within the wor
# then search the possible matches for precise matches using the slower but more precise method
# need to use .loc instead of .iloc as it can take boolean input (.iloc only takes index numbers)
precise_matches = possible_matches.loc[possible_matches.within(polygon)]

# how many rows are left now?
print(f"Filtered wells: {len(precise_matches.index)}")

# REBUILDING SPATIAL INDEX
# this needs to be done as we have reduced the amount of data but the spatial index still has the original amount
# rebuild the spatial index using the new, smaller dataset
geoms = precise_matches.geometry.to_list()

idx = STRtree(geoms)