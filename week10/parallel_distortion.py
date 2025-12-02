# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 11:30:57 2025

@author: k67630sc
"""

"""
* Script to evaluate which of the Equal Area projections recommended by 
*		projectionwizard.org is the best for use in Iceland
"""
from pandas import DataFrame
from time import perf_counter
from geopandas import read_file
from week5 import evaluate_distortion
from pyproj import Geod, CRS, Transformer
from concurrent.futures import ProcessPoolExecutor, as_completed

def distortion_worker(geo_string, proj_string, g, minx, miny, maxx, maxy, minr=10000, maxr=1000000, samples=10000):

    # construct transformer
    transformer = Transformer.from_crs(CRS.from_proj4(geo_string), CRS.from_proj4(proj_string), always_xy=True)

    return evaluate_distortion(g, transformer, minx, miny, maxx, maxy, minr, maxr, samples)

# main code block
if __name__ == "__main__":

    # make a list of dictionaries storing the projections to evaluate
    projections = [
        {'name':'Mollweide', 'proj':'+proj=moll +lon_0=0 +datum=WGS84 +units=m +no_defs'},
        {'name':'Hammer', 'proj':"+proj=hammer +lon_0=0 +datum=WGS84 +units=m +no_defs"},
        {'name':'Equal Earth', 'proj':"+proj=eqearth +lon_0=0 +datum=WGS84 +units=m +no_defs"},
        {'name':'Eckert IV', 'proj':"+proj=eck4 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"},
        {'name':'Wagner IV', 'proj':"+proj=wag4 +lon_0=0 +datum=WGS84 +units=m +no_defs"},
        {'name':'Wagner VII', 'proj':"+proj=wag7 +lon_0=0 +datum=WGS84 +units=m +no_defs"}]

    # set the geographical proj string and ellipsoid (should be the same)
    geo_string = "+proj=longlat +datum=WGS84 +no_defs"
    g = Geod(ellps='WGS84')

    # load the shapefile of countries and extract country of interest
    world = read_file("../../data/natural-earth/ne_10m_admin_0_countries.shp")

    # get the country we want to map
    country = world.loc[world.ISO_A3 == "ISL"]

    # get the bounds of the country
    minx, miny, maxx, maxy = country.total_bounds

    # start timer
    start = perf_counter()

    # initialise a PyProj Transformer to transform coordinates
    results = DataFrame(projections)
    for idx, p in results.iterrows():

        # get proj string
        proj_string = p['proj']

    # print the results, sorted by area distortion
    #print(DataFrame(results).sort_values('Ea'))
    print(f"\nCompleted in {perf_counter() - start:.2f} seconds.")