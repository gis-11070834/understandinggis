# importing the open function of rasterio and using the 'as' to rename it to less generic name
from rasterio import open as rio_open
from rasterio.transform import rowcol, xy

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
    
    # print out the elevation at that location by reading it from the dataset
    print(f"{dem_data[coord_2_img(dem.transform, x, y)]:.0f}m")
  
# once you leave the block, the file automatically closes for you