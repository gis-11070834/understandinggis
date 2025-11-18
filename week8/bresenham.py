# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 11:37:05 2025

@author: k67630sc
"""

from numpy import zeros, column_stack
from rasterio import open as rio_open
from rasterio.plot import show as rio_show
from rasterio.transform import rowcol
from matplotlib.pyplot import subplots, savefig
from matplotlib.colors import LinearSegmentedColormap
from skimage.draw import line

def coord_2_img(transform, x, y):
    """
    Convert from coordinate space to image space using
    the affine transform object from a rasterio dataset
    
    """
    r, c = rowcol(transform, x,y)
    return int(r), int(c)
    

LOCATION = (334170, 515165)

# open the elevation data file
with rio_open("../../data/helvellyn/Helvellyn-50.tif") as dem:

    # read the data out of band 1 in the dataset
    dem_data = dem.read(1) # COMPLETE THIS LINE

    # create a new 'band' of raster data the same size
    output = zeros(dem_data.shape) # COMPLETE THIS LINE

    # storing image space coordinates of the coordinate space coordinates in row and col
    row, col = coord_2_img(dem.transform, 334170, 515165)
    
    # set the pixel at specified location to 1
    dem_data[dem.index(334170, 515165)] = 1
    
    print(column_stack(line(row, col, row, col+50)))
    
    for r, c in column_stack(line(row, col, row, col+50)):
        
        output[r, c] = 1

# plot the dataset
fig, my_ax = subplots(1, 1, figsize=(16, 10))

# add the DEM
rio_show(
  dem_data,
  ax=my_ax,
  transform = dem.transform,
)
# add the drawing layer
rio_show(
    output,
    ax=my_ax,
    transform=dem.transform,
    cmap = LinearSegmentedColormap.from_list('binary_viewshed', [(0, 0, 0, 0), (1, 0, 0, 0.5)], N=2)
    )
savefig('./out/bresenham.png', bbox_inches='tight')

