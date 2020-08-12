##
# Some testing with bit manipulation in python
#

import random

n = []

for i in range(10) :
    n.append(random.randint(-30, 30))

print(str(n))
print(bytes(str(n), 'utf-8'))
print(str(bytes(str(n), 'utf-8')))

exit(0)

num = '12ab34cd'

b = bytes.fromhex(num)
print(b, type(b))

# Now to do some bit-shifting
print(b[0], type(b[0]))

byte = b[0]
# Get the 4 msbs:
print(byte >> 4 & 0b1111)

# Get the 4 lsbs:
print(byte & 0b1111)

byte = b[1]
print(byte >> 4 & 0b1111)
print(byte & 0b1111)