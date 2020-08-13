##
# Python program to call a simple c function
#

import ctypes    # this module allows us to call c functions (probably)

# so_file = "./function.so"
so_file = "./function.o"
my_function = ctypes.CDLL(so_file)

print(type(my_function))
my_function.main()