# -*- coding: utf-8 -*-
"""
Created on Fri Nov  7 14:18:40 2025

@author: k67630sc
"""
from numpy.random import uniform
from numpy import arange
from math import radians, cos, sin, hypot
from shapely.geometry import Polygon
from pyproj import Geod, Transformer

def compute_offset(origin, distance, direction):
    """
    Compute the location of a point at a given distance and direction from a specified location using trigonometry
    """
    offset_x = origin[0] + cos(radians(direction)) * distance	# COMPLETE THIS LINE
    offset_y = origin[1] + sin(radians(direction)) * distance	# COMPLETE THIS LINE 
    return (offset_x, offset_y)

def evaluate_distortion(g, transformer, minx, miny, maxx, maxy, minr, maxr, sample_number=1000, vertices=16):
   
    # calculate the required number of random locations (x and y separately) plus radius
    xs = uniform(low=minx, high=maxx, size=sample_number)
    ys = uniform(low=miny, high=maxy, size=sample_number)
    rs = uniform(low=minr, high=maxr, size=sample_number)
    
    # offset distances
    forward_azimuths = arange(0, 360, 22.5) # arrange function similar to range but permits non-integer
    
    # looping through out random points and radii
    area_indicies = []
    shape_indicies = []
    distance_indicies = []
    
    for x, y, r in zip(xs, ys, rs):
    
        # building our random circles
        # construct a circle around the centre point on the ellipsoid
        lons, lats = g.fwd([x]*vertices, [y]*vertices, forward_azimuths, [r]*vertices)[:2]
    
        # project the result, calculate area, append to the list
        # direction='FORWARD' means we transform from geographical to projected coordinates - would be 'BACKWARD' for opposite
        e_coords = [ transformer.transform(lon, lat, direction='FORWARD') for lon, lat in zip(lons, lats) ]
        # get the area of the resulting circle
        ellipsoidal_area = Polygon(e_coords).area
    
        # create a circle on the projection plane
        # transform the centre point to the projected CRS
        centre_x, centre_y = transformer.transform(x, y, direction='FORWARD')
        # construct a circle around the projected point on a plane, calculate area
        planar_area = Polygon([compute_offset((centre_x, centre_y), r, az) for az in forward_azimuths]).area
    
        # Calculating the area and shape distortion values
        # now that we have an ellipsoidal and projected circle we want to calculate the distortion value
        # done via a = (Si - S'i/Si + S'i)
        area_indicies.append(abs(ellipsoidal_area - planar_area) / (abs(ellipsoidal_area + planar_area)))
    
        # get radial distances from the centre to each of the 16 points on the circle
        ellipsoidal_radial_distances = [ hypot(centre_x - ex, centre_y - ey) for ex, ey in e_coords ]

        # get the absolute proportional difference between the expected and actual radial distance for each 'spoke'
        shape_distortion = [abs((1 / vertices) - (d / sum(ellipsoidal_radial_distances))) for d in ellipsoidal_radial_distances]
        
        # append the sum of the list to the shape_indicies list
        shape_indicies.append(sum(shape_distortion))
        
    #print(len(area_indicies), len(shape_indicies)) - checking the length of the indicies
    
    # Turn the list of indicies into a single value for the map
    Ea = 1 / sample_number * sum(area_indicies)
    Es = 1 / sample_number * sum(shape_indicies)
    
    # find distance distortion
    for _ in range(sample_number):
        xs = uniform(low=minx, high=maxx, size=2)
        ys = uniform(low=miny, high=maxy, size=2)
        
        # calculate the distance along the ellipsoid
        ellipsoidal_distance = g.line_length(xs, ys)
        
        #print(ellipsoidal_distance)
   
       # add two transformer.transform() statements to project both of your random locations
        origin = transformer.transform(xs[0], ys[0], direction='FORWARD')
        destination =  transformer.transform(xs[1], ys[1], direction='FORWARD')
        planar_distance= hypot(origin[0] - destination [0], origin[1] - destination[1])
        
        #calculate distance index
        distance_indicies.append(abs(ellipsoidal_distance - planar_distance) / (abs(ellipsoidal_distance + planar_distance)))
        
    # calculate Ep
    Ep = 1 / sample_number * sum(distance_indicies)
    
    # calibrate and return all of the measures
    return Ep, Es, Ea


# Calculating distortion of CRS

# initialise a pyproj transformer to transform coordinates
transformer = Transformer.from_crs(world.crs, estimated_crs, always_xy=True)

#finding the bounds for the distortion and plot
minx, miny, maxx, maxy = shortest_border_GS.total_bounds

# calculate the distortion
Ep, Es, Ea = evaluate_distortion(g, transformer, minx, miny, maxx, maxy, 10000, 1000000, 1000)

print(f"\t Local UTM CRS - {estimated_crs}")
print(f"\t{'Distance distortion (Ep):':<26}{Ep:.6f}")
print(f"\t{'Shape distortion (Es):':<26}{Es:.6f}")
print(f"\t{'Area distortion (Ea):':<26}{Ea:.6f}\n")