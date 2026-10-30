import  os

my_file = 'test.txt'
##Reading from a file the total number of characters
f = open(my_file)
lines = f.readlines()
sum=0
print(lines)
for line in lines:
    line = line.strip()
    ct=len(line)
    sum = sum+ct
    # print(line, end='')
f.close()

print(sum)