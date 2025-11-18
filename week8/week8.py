from numpy import zeros, column_stack
from rasterio import open as rio_open
from rasterio.plot import show as rio_show
from rasterio.transform import rowcol, xy
from sys import exit
from skimage.draw import line, circle_perimeter
from math import hypot

def coord_2_img(transform, x, y):
    """ 
    * Convert from coordinate space to image space using the 
    * 	Affine transform object from a rasterio dataset
    *
    * Note that rowcol() returns floats so they need to be 
    * 	converted to integers to be used as cell references
    """
    r, c = rowcol(transform, x, y)
    return (int(r), int(c))

def line_of_sight(r0, c0, height0, r1, c1, height1, radius, dem_data, transform, output):
    
    """ Calculates line of sight to each location on the circle, updating each cell line
    works out the visibility of each point on a line from the origin to that location
    
    Calculate Dy/Dx at each cell - if it is greater than any previous Dy/Dx value then the
    cell is visible and we set the value to 1 in the output dataset. if not its not visible
    and the cell remains at 0
    """
    
    # init variable for biggest dydx so far (starts at -infinity which is smaller than any possible number)
    max_dydx = -float('inf') 	

    # loop along the pixels in the line (excluding the first one)
    # column_stack converts the index into a single array of coordinate pairs and the use of list slicing excldes the first element from the loop
    for r, c in column_stack(line(r0, c0, r1, c1))[1:]:
        
        # calculating the distance between origin point and curent point
        dx = hypot(r - r0, c - c0)
        
        #if we go too far, or go off the edge of the data, stop looping
        if dx > radius or not 0 <= r < dem_data.shape[0] or not 0 <= c < dem_data.shape[1]:
            break
    
    	# calculate the current value for dy / dx
        base_dydx = (dem_data[(r, c)] - height0) / dx
        tip_dydx = (dem_data[(r, c)] + height1 - height0) / dx
    
        # if the tip dydx is bigger than the previous max, it is visible
        if (tip_dydx > max_dydx):
            output[(r, c)] = 1

		# if the base dydx is bigger than the previous max, update
        max_dydx = max(max_dydx, base_dydx)

	# return updated output surface
    return output

def viewshed(x0, y0, radius_m, observer_height, target_height, dem_data, transform):

    """Algorithm calculates a circle using the Midpoint Circle Algorithm
    will work out the end point for each line of sight
    """
    r0, c0 = coord_2_img(transform, x0, y0)
    
    output = zeros(dem_data.shape)
    
    # make sure that we are within the dataset (larger than 0 and smaller than height/width of dataset)
    # .shape returns the height and width of the dataset
    if not 0 <= r0 < dem_data.shape[0] or not 0 <= c0 < dem_data.shape[1]:
        print(f"Sorry, {x0, y0} is not within the elevation dataset.")
        exit()
    
    # convert the radius (m) to pixels by dividing it by the resolution of the dataset
    radius_px = int(radius_m / transform[0])
    
	# get the observer height (above sea level)
    height0 = dem_data[r0, c0] + observer_height
    
    # get pixels in the perimeter of the viewshed
    for r, c in column_stack(circle_perimeter(r0, c0, radius_px)):

        # calculate line of sight to each pixel, pass output and get a new one back each time
        output = line_of_sight(r0, c0, height0, r, c, target_height, radius_px, dem_data, transform, output)

    # return the resulting viewshed
    return output 
    
# set origin for viewshed
x0, y0 = 330000, 512500

# open the elevation data file
with rio_open("../../data/helvellyn/Helvellyn-50.tif") as dem:
    
    # read the data out of band 1 in the dataset
    dem_data = dem.read(1) 
    
    # transformed origin into image space
    r0, c0 = coord_2_img(dem.transform, x0, y0)
    
    # create a new 'band' of raster data the same size which is transparent
    output = zeros(dem_data.shape)
    
    # setting the value of the viewshed origin to 1 in the output surface
    output[r0, c0] = 1 
    
    # calculate the viewshed
    output = viewshed(x0, y0, 20000, 1.8, 100, dem_data, dem.transform)