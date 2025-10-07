# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 13:12:22 2025

@author: k67630sc
"""

from geopandas import read_file, GeoSeries

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