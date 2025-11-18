from numpy import zeros, column_stack
from rasterio import open as rio_open
from rasterio.plot import show as rio_show
from rasterio.transform import rowcol, xy
from sys import exit
from skimage.draw import line, circle_perimeter
from math import hypot
from math import floor, ceil
from geopandas import GeoSeries
from shapely.geometry import Point
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from rasterio.plot import show as rio_show
from matplotlib.pyplot import subplots, savefig
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.colors import LinearSegmentedColormap

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

# output image
fig, my_ax = subplots(1, 1, figsize=(16, 10))
my_ax.set_title("Viewshed Analysis")

	# draw dem
rio_show(
	dem_data,
	ax=my_ax,
	transform = dem.transform,
	cmap = 'viridis',
	)

	# draw dem as contours
rio_show(
	dem_data,
	ax=my_ax,
	contour=True,
	transform = dem.transform,
	colors = ['white'],
	linewidths = [0.5],
	)

# add viewshed
rio_show(
	output,
	ax=my_ax,
	transform=dem.transform,
	cmap = LinearSegmentedColormap.from_list('binary_viewshed', [(0, 0, 0, 0), (1, 0, 0, 0.5)], N=2)
	)

# add origin point
GeoSeries(Point(x0, y0)).plot(
	ax = my_ax,
	markersize = 60,
	color = 'black',
	edgecolor = 'white'
	)

# add a colour bar
fig.colorbar(ScalarMappable(norm=Normalize(vmin=floor(dem_data.min()), vmax=ceil(dem_data.max())), cmap='viridis'), ax=my_ax, pad=0.01)

# add north arrow
x, y, arrow_length = 0.97, 0.99, 0.1
my_ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
	arrowprops=dict(facecolor='black', width=5, headwidth=15),
	ha='center', va='center', fontsize=20, xycoords=my_ax.transAxes)

# add scalebar
my_ax.add_artist(ScaleBar(dx=1, units="m", location="lower right"))

# add legend for point
my_ax.legend(
	handles=[
		Patch(facecolor=(1, 0, 0, 0.5), edgecolor=None, label=f'Visible Area'),
		Line2D([0], [0], marker='o', color=(1,1,1,0), label='Viewshed Origin', markerfacecolor='black', markersize=8)
	], loc='lower left')

# save the result
savefig('./out/7.png', bbox_inches='tight')
print("done!")