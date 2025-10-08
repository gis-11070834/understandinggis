# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 13:12:22 2025

@author: k67630sc
"""

from geopandas import read_file, GeoSeries
from matplotlib.pyplot import subplots, savefig, title
from pyproj import Geod

# load the shapefile of countries - this gives a table of 12 columns and 246 rows (one per country)
world = read_file("../../data/natural-earth/ne_10m_admin_0_countries.shp")

# print a list of all of the columns in the shapefile
print(world.columns)

#the name column of data in set isnt always standardised so ISO_A3 is used as it is
#use the .loc property of GDF object to extract a new GDF containy only the country for which the ISO3 code is USA
#.loc exposes the underlying data in a way that allows you to select rows from it using a query (aka is world,ISO3 == USA true)
#important - equality operator is == not = wich is an assignment operator (variables)
# extract the country rows as a GeoDataFrame object with 1 row
usa = world.loc[(world.ISO_A3 == 'USA')]

print(type(usa))

# extract the geometry columns as a GeoSeries object
#use .geometry to extract the geometry column as a geoseries
#a geoseries object in geopandas represents a column of geometry features without any attribute data attached to it
usa_col = usa.geometry

print(type(usa_col))

# extract the geometry objects themselves from the GeoSeries
#extract the value from the row gotten from above using .iloc (index location) property - exposes underlying data to select it using a number to represent the row ID
usa_geom = usa_col.iloc[0]

print(type(usa_geom))

#now we repeat the same process for mexico (MEX)
mex = world.loc[world.ISO_A3 == 'MEX']
print(type(mex))

mex_col = mex.geometry
print(type(mex_col))

mex_geom = mex_col.iloc[0]
print(type(mex_geom))

# the .intersection() function finds the intersection between the two geometries stores in the new variable border
# calculate the intersection of the geometry objects
border = usa_geom.intersection(mex_geom)

print(border)

# create map axis object
my_fig, my_ax = subplots(1, 1, figsize=(16, 10))

# remove axes
my_ax.axis('off')

# plot the border
GeoSeries(border).plot(
  ax = my_ax
	)

# save the image
savefig('./out/first-border.png') 

# measuring the length of the border

# set which ellipsoid you would like to use
# this function creates a geodesy object based on WGS84 (a common general model for the shape of the earth) stored in variable g
# this is important as earth is an ellipsoid, so measurements will be different. also gives access to vincenty equations for measuring on an ellipsoid
g = Geod(ellps='WGS84')

#this prints a MultiLineString,in which segments (LineString) are defined by start and end point - the end of one segment will be the same as the start point of the next
# to work out the length of the border need o work out the length of each of these segments and add them up through loops 
# loop through each segment, measure the distance between the start and end point and add it to running total (length of wall)
print(border)

# loop through each segment in the line and print the coordinates
for segment in border.geoms:
	print(f"from:{segment.coords[0]}\tto:{segment.coords[1]}")
    
# initialise a variable to hold the cumulative length
cumulative_length = 0

# loop through each segment in the line
for segment in border.geoms:

	# the segment.coords[0] means start and the next [0] defines longitude, the segment.coord[1] signifies end and second [1] signifies latitude and other way around
	distance = g.inv(segment.coords[0][0], segment.coords[0][1], segment.coords[1][0], segment.coords[1][1])[2]

	# add the distance to our cumulative total
	cumulative_length += distance

print(cumulative_length)


