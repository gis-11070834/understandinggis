from math import radians, cos, sin, hypot	# IMPORT NECESSARY FUNCTIONS HERE
from geopandas import read_file
from pyproj import Geod, CRS, Transformer
from numpy.random import uniform
from numpy import arange
from shapely.geometry import Polygon

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
    
    print(Ea, Es)
    
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
    
        #calculate ice area
        ice_area_km2 = ice.to_crs(projection['proj']).geometry.area.sum() / 1000000
   
        # report to user
        print(f"\n{projection['name']} ({projection['description']})")
        print(f"\t{'Distance distortion (Ep):':<26}{Ep:.6f}")
        print(f"\t{'Shape distortion (Es):':<26}{Es:.6f}")
        print(f"\t{'Area distortion (Ea):':<26}{Ea:.6f}")
        print(f"\t{'Ice Area:':<26}{ice_area_km2:,.0f} km sq.")