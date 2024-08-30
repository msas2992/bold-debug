import pygatt
import binascii

# adapter = pygatt.BGAPIBackend(serial_port='COM12')


# adapter.start()
# device = adapter.connect('')


YOUR_DEVICE_ADDRESS = "EE6498195A3A"
# Many devices, e.g. Fitbit, use random addressing - this is required to
# connect.
ADDRESS_TYPE = pygatt.BLEAddressType.random

dongle = pygatt.BGAPIBackend(serial_port='COM12')
dongle.start()

dut = dongle.connect(YOUR_DEVICE_ADDRESS, address_type=ADDRESS_TYPE)

for uuid in dut.discover_characteristics().keys():
    try:
        print("Read UUID %s: %s" % (uuid, binascii.hexlify(dut.char_read(uuid))))
    except:
        pass
