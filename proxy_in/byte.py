##
# testing to see how byte objects work in python
#



payload = b'\xf0\x12\x01\xab'
print(payload, type(payload))

print(payload[1])
print(payload[0])
print(payload[2])
print(payload[3])