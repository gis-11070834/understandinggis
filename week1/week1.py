from geopandas import read_file 
from matplotlib.pyplot import subplots, savefig

world = read_file("../../data/natural-earth/ne_50m_admin_0_countries.shp")
print(world.columns)
graticule = read_file("../../data/natural-earth/ne_110m_graticules_15.shp")
bbox = read_file("../../data/natural-earth/ne_110m_wgs84_bounding_box.shp")

print(world.head())
#first we imported the read_file from the geopandas libary into a geodataframe, this was used to turn the ne_50m_admin into an object, stored in the variable world. Then we look at the first 5 rows of code with the .head function of variable world
# create map axis object
my_fig, my_ax = subplots(1, 1, figsize=(16, 10))

# add bounding box and graticule layers
bbox.plot(
    ax = my_ax,
    color = 'lightblue',
    linewidth = 0,
    )

# plot the countries
world.plot(								# plot the world dataset
    ax = my_ax,						# specify the axis object to draw it to
    column = 'POP_EST',		# specify the column used to style the dataset
    cmap = 'OrRd',				# specify the colour map used to style the dataset based on POP_EST
    scheme = 'quantiles',	# specify how the colour map will be mapped to the values in POP_EST
    linewidth = 0.5,			# specify the line width for the country outlines
    edgecolor = 'gray',		# specify the line colour for the country outlines
    )

# plot the graticule
graticule.plot(
    ax = my_ax,
    color = 'white',
    linewidth = 0.5,
    )

# turn off the visible axes on the map
my_ax.axis('off')
# save the result
savefig('week1/out/1.png')
print("done!") 