# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 13:12:22 2025

@author: k67630sc
"""

from geopandas import read_file, GeoSeries
from matplotlib.pyplot import subplots, savefig, title
from pyproj import Geod
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.lines import Line2D
from matplotlib.patches import Patch 

# load the shapefile of countries - this gives a table of 12 columns and 246 rows (one per country)
world = read_file("../../data/natural-earth/ne_10m_admin_0_countries.shp")
graticule = read_file("../../data/natural-earth/ne_110m_graticules_5.shp")

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

#making it into a map

lambert_conic = ("+proj=lcc +lon_0=-108.8085937 +lat_1=25.8689313 +lat_2=36.462161 +lat_0=31.1655461 +datum=WGS84 +units=m +no_defs")

# create map axis object
my_fig, my_ax = subplots(1, 1, figsize=(16, 10))

# remove axes
my_ax.axis('off')

# set title
title(f"Trump's wall would have been {cumulative_length / 1000:.2f} km long.")

# project border
# NOTE - we had to transform all datasets into Lamber Conformal Conic project using the .to_crs() function of the GDF geoseries object
# also set Geoseries using constructor into the same thing as CRS using world dataset before transforming
border_series = GeoSeries(border, crs=world.crs).to_crs(lambert_conic)

# extract the bounds from the (projected) GeoSeries Object
minx, miny, maxx, maxy = border_series.geometry.iloc[0].bounds

# set bounds (10000m buffer around the border itself, to give us some context)
buffer = 10000
my_ax.set_xlim([minx - buffer, maxx + buffer])
my_ax.set_ylim([miny - buffer, maxy + buffer])

#explanation of code above
#setting bounds of the output maps to match the bounds of the border layer - constrain to area needed to show
#first line uses variable expansion .bounds returns a list of 4 values [minx,miny,maxx,maxy] which python expands into 4 variables
#add a 'buffer# of 10km to each side of the bounds to stop the border touching the edge of the map

# plot data
usa.to_crs(lambert_conic).plot(
    ax = my_ax,
    color = '#ccebc5',
    edgecolor = '#4daf4a',
    linewidth = 0.5,
    )
mex.to_crs(lambert_conic).plot(
    ax = my_ax,
    color = '#fed9a6',
    edgecolor = '#ff7f00',
    linewidth = 0.5,
    )
border_series.plot(     # note that this has already been projected above!
    ax = my_ax,
    color = '#984ea3',
    linewidth = 2,
    )
graticule.to_crs(lambert_conic).plot(
    ax=my_ax,
    color='grey',
    linewidth = 1,
    )

# add north arrow
x, y, arrow_length = 0.98, 0.99, 0.1
my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
	arrowprops=dict(facecolor='black', width=5, headwidth=15),
	ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)

# add scalebar
my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower left", length_fraction=0.25))

# add legend
my_ax.legend(handles=[
        Patch(facecolor='#ccebc5', edgecolor='#4daf4a', label='USA'),
        Patch(facecolor='#fed9a6', edgecolor='#ff7f00', label='Mexico'),
        Line2D([0], [0], color='#984ea3',  lw=0.6, label='Border')
    ],loc='lower right')

# save the result
savefig('out/2.png', bbox_inches='tight')
print("done!")