# importing the open function of rasterio and using the 'as' to rename it to less generic name
from rasterio import open as rio_open
from rasterio.transform import rowcol, xy
from rasterio.plot import show as rio_show
from matplotlib.pyplot import subplots, savefig
from numpy import zeros
from matplotlib.colors import LinearSegmentedColormap

def coord_2_img(transform, x, y):
	""" 
	* Convert from coordinate space to image space using the 
	* 	Affine transform object from a rasterio dataset
	"""
	r, c = rowcol(transform, x, y)
	return (int(r), int(c))

# open the raster dataset
with rio_open("../../data/helvellyn/Helvellyn-50.tif") as dem:
	
    # read the data out of band 1 in the dataset
    dem_data = dem.read(1)
    
    # create a new 'band' of raster data the same size
    output = zeros(dem_data.shape)
    
    # set the cell at coordinates of helvellyn to 1 to colour it in
    dem_data[dem.index(334170, 515165)] = 1
    
# plot the dataset
fig, my_ax = subplots(1, 1, figsize=(16, 10))

# add the DEM
rio_show(
    dem_data,
    ax=my_ax,
    transform = dem.transform,
    )

# add the empty layer
rio_show(
    output,
    ax=my_ax,
    transform=dem.transform,
    cmap = LinearSegmentedColormap.from_list('binary',
    [(0, 0, 0, 0), (0, 0.5, 1, 0.5)], N=2)
    )

# save the resulting map
savefig('./out/6.png', bbox_inches='tight')
  
# once you leave the block, the file automatically closes for you