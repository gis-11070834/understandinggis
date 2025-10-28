from math import radians, cos, sin	# IMPORT NECESSARY FUNCTIONS HERE
from geopandas import read_file
from pyproj import Geod, CRS, Transformer
from numpy.random import uniform

def compute_offset(origin, distance, direction):
    """
    Compute the location of a point at a given distance and direction from a specified location using trigonometry
    """
    offset_x = origin[0] + cos(radians(direction)) * distance	# COMPLETE THIS LINE
    offset_y = origin[1] + sin(radians(direction)) * distance	# COMPLETE THIS LINE 
    return (offset_x, offset_y)

    

# using __main__ to only run main code when needed, not when functions being called when code used as a library in future
if __name__ == "__main__":
    
   # creating a geodateframe of all of the countries in the world variable
   world = read_file("../../data/natural-earth/ne_10m_admin_0_countries.shp")
   # extracting the iceland row from the GeoDataFrame
   iceland = world.loc[(world.ISO_A3 == 'ISL')]
   # creating a geodataframe of the land cover in iceland
   land_cover = read_file ("../../data/iceland/gis_osm_natural_a_free_1.shp")
   # finding the areas covered in ice through finding rows = glacier
   ice = world.loc[land_cover.fclass == "glacier"]
   
  
   # get the bounds of the country
   minx, miny, maxx, maxy = iceland.total_bounds
   
   # DEFINING OUR GEODESIC MODEL AND CRS
   # set the geographical proj string and ellipsoid (should be the same)
   geo_string = "+proj=longlat +datum=WGS84 +no_defs"
   g = Geod(ellps='WGS84')
   
   # create a list of dictionaries for the projected CRS' to evaluate for distortion
   projections = [
    {'name':"Web Mercator", 'description':"Global Conformal",   'proj':"+proj=merc +a=6378137 +b=6378137 +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +k=1 +units=m +nadgrids=@null +wktext +no_defs +type=crs"},
    {'name':"Eckert IV",    'description':"Global Equal Area",  'proj':"+proj=eck4 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs"},
    {'name':"Albers' Conic", 'description':"Local Equal Area",  'proj':"+proj=aea +lon_0=-18.8085937 +lat_1=63.3985599 +lat_2=66.4577209 +lat_0=64.9281404 +datum=WGS84 +units=m +no_defs"}
   ]
    
   # CALCULATING DISTORTION FOR EACH PROJECTION
    # loop through each CRS
    # variable expansion - eneumerate() provides the count variable (in this case ax_num which contains values 0,1,2) and projection will contain the dictionary containing the current projection information
   for ax_num, projection in enumerate(projections):
        
        #print(f"Processing projection {ax_num} {projection['name']}")
        # initialise a PyProj Transformer to transform coordinates
        # extract proj value from the projection dictionary
        # uses 2 .crs to do (one for lat one for long) and need to force the order xy (sometimes in opposite order)
        transformer = Transformer.from_crs(CRS.from_proj4(geo_string), CRS.from_proj4(projection['proj']), always_xy=True)
        
        # calculate the distortion
        Ep, Es, Ea = evaluate_distortion(g, transformer, minx, miny, maxx, maxy, 10000, 1000000, 1000)
       