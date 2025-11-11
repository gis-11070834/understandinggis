# importing the open function of rasterio and using the 'as' to rename it to less generic name
from rasterio import open as rio_open
from rasterio.transform import rowcol, xy

def coord_2_img(transform, x, y):
    """ 
    * Convert from coordinate space to image space using the 
    * 	Affine transform object from a rasterio dataset
    *
    * Note that rowcol() returns floats so they need to be 
    * 	converted to integers to be used as cell references
    """
    row, col = rowcol(transform, x, y)
    return (int(row), int(col))

# open a raster file into a variable called dem
with rio_open('../../data/helvellyn/Helvellyn-50.tif') as dem:

	# everything inside the with block can access dem
    # print(dem.profile)
    
    # get the single data band from a dem
    band_1 = dem.read(1)
    dem_data = band_1
    
    # transform the coordinates for the summit of Helvellyn into image space
    #row, col = coord_2_img(dem.transform, 334170, 515165)

    # print out the elevation at that location by reading it from the dataset
    #print(f"{dem_data[row][col]:.0f}m")	# note that this makes use of an f-string to format the number

    # print out the elevation at that location by reading it from the dataset
    print(f"{dem_data[coord_2_img(dem.transform, 334170, 515165)]:.0f}m")
  
# once you leave the block, the file automatically closes for you