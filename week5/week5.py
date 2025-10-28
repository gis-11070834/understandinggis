from math import radians, cos, sin	# IMPORT NECESSARY FUNCTIONS HERE
from geopandas import read_file

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
      
   print(iceland.total_bounds)