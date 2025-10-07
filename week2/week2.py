# create a variable that holds a list of three words
words = ['First', 'Second', 'Third']

# print each of those words in turn
for word in words:
	# everything in the indented block is run for each of the 3 elements in the list
	print(word)
print(list(range(10)))
# loop through a list 0-2
for i in range(3):
     print(i)
for i in range(3):
     print(i, words[i])
     
# here is your list of numbers
numbers = [1,2,3,4,5,6,7,8,9,10,15,30]

# this variable will hold your result, start it at 0
total = 0

# MISSING LINE HERE
for n in numbers:
    
    
# loop through the list

	# INCOMPLETE LINE HERE
    
	# add each number to the total
	total += n #+= add to the existing variable defined

# print the result
print(total)