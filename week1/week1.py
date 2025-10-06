from geopandas import read_file 
from matplotlib.pyplot import subplots, savefig
world = read_file("../../data/natural-earth/ne_50m_admin_0_countries.shp")

print(world.head())
#first we imported the read_file from the geopandas libary into a geodataframe, this was used to turn the ne_50m_admin into an object, stored in the variable world. Then we look at the first 5 rows of code with the .head function of variable world
# create map axis object
my_fig, my_ax = subplots(1, 1, figsize=(16, 10))

# plot the countries onto ax
world.plot(ax = my_ax)
# turn off the visible axes on the map
my_ax.axis('off')
# save the result
savefig('week1/out/1.png')
print("done!")