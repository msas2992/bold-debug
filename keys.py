import base64
import os

filename = 'C:\\projects\\BOLD_SecureLock\\Firmware\\devicekeys_example_09042020.csv'

lines = open(filename, 'r').readlines()

for line in lines:
    if line.startswith('device'):
        continue

    elements = line.strip().split(',')

    deviceid = '{:016X}'.format(int(elements[0]))
    keys = []
    for i in range(4):
        key = list(base64.b64decode(elements[i+1]))
        # privateKey = base64.b64decode(elements[i+1]).hex()
        key.reverse()
        key = bytes(key).hex()
        keys.append(key)
        # privateKeyReversed = "".join(reversed([privateKey[i:i+2] for i in range(0, len(privateKey), 2)]))
        # print(key, privateKeyReversed)

    print(deviceid, keys)

    # print(deviceid, key1, key2, key3, key4)
