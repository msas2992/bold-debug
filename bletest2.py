import time
import pygatt
import binascii
from pprint import pprint
import struct

# dongle = pygatt.BGAPIBackend(serial_port='COM12')
# dongle.start()

# ADDRESS_TYPE = pygatt.BLEAddressType.random
# devices = dongle.scan(run_as_root=True, timeout=2)

# UUID_DEVICE_NAME = '00002a00-0000-1000-8000-00805f9b34fb'

# for device in devices:
#     print(device['address'], device['rssi'])
#     address = device['address']

#     if device['rssi'] < -50:
#         print('low rssi, skipping')
#         continue

#     try:
#         device = dongle.connect(address, address_type=ADDRESS_TYPE)
#         try:
#             devicename = device.char_read(UUID_DEVICE_NAME).decode()
#         except:
#             continue
#         print(devicename)
#         device.disconnect()
#     except pygatt.exceptions.NotConnectedError:
#         print("failed to connect to %s" % address)
#         continue

def ble_find_device(devname, target_address=None):
    dongle = pygatt.BGAPIBackend(serial_port='COM12')
    dongle.start()

    ADDRESS_TYPE = pygatt.BLEAddressType.random
    devices = dongle.scan(run_as_root=True, timeout=2)

    UUID_DEVICE_NAME = '00002a00-0000-1000-8000-00805f9b34fb'

    pprint(devices)
    for device in devices:
        # print(device['address'], device['rssi'])
        address = device['address']

        if address == target_address:
            data = device['packet_data']['connectable_advertisement_packet']['manufacturer_specific_data']
            print(data)
            fields = struct.unpack('>HBBBQB', data.decode())
            print(fields)
            break
        else:
            continue

        if device['rssi'] < -50:
            # print('low rssi, skipping')
            continue

        try:
            bledevice = dongle.connect(address, address_type=ADDRESS_TYPE)
            try:
                devicename = bledevice.char_read(UUID_DEVICE_NAME).decode()
            except:
                continue
            print(devicename, address, device['rssi'])
            if devicename == devname:
                return device['rssi']
            bledevice.disconnect()
        except pygatt.exceptions.NotConnectedError:
            # print("failed to connect to %s" % address)
            continue

    return False

if __name__ == '__main__':
    address = 'EE:64:98:19:5A:3A'
    ble_find_device('', address)