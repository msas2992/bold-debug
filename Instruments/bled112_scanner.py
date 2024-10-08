#!/usr/bin/env python

""" Barebones BGAPI scanner script for Bluegiga BLE modules

This script is designed to be used with a BGAPI-enabled Bluetooth Smart device
from Bluegiga, probably a BLED112 but anything that is connected to a serial
port (real or virtual) and can "speak" the BGAPI protocol. It is tuned for
usable defaults when used on a Raspberry Pi, but can easily be used on other
platforms, including Windows or OS X.

Note that the command functions do *not* incorporate the extra preceding length
byte required when using "packet" mode (only available on USART peripheral ports
on the BLE112/BLE113 module, not applicable to the BLED112). It is built so you
can simply plug in a BLED112 and go, but other kinds of usage may require small
modifications.

Changelog:
    2013-04-07 - Fixed 128-bit UUID filters
               - Added more verbose output on startup
               - Added "friendly mode" output argument
               - Added "quiet mode" output argument
               - Improved comments in code
    2013-03-30 - Initial release

"""

__author__ = "Jeff Rowberg"
__license__ = "MIT"
__version__ = "2013-04-07"
__email__ = "jeff@rowberg.net"

import sys, optparse, serial, struct, time, datetime, re, signal, string
from collections import deque

filter_uuid = []
filter_mac = []
filter_rssi = 0


class BLE_Scanner():
    def __init__(self):
        pass

    def connect(self, comport):
        try:
            self.serial = serial.Serial(port=comport, baudrate=115200, timeout=1)
        except serial.SerialException as e:
            return False

        # flush buffers
        self.serial.flushInput()
        self.serial.flushOutput()
        return True

    def scan2(self, deviceToFind):
        sp=False
        while 1:
            try:
                b = self.serial.read()
                if sp:
                    print(b)
            except:
                pass

            d = bgapi_parse(ord(b), '')
            if d is not None:
                print(d)
                sp = True


    def scan(self, deviceToFind, timeout=1):
        start = time.time()
        while True:
            while self.serial.inWaiting():
                data = bgapi_parse(ord(self.serial.read()), deviceToFind)

                if data is not None:
                    # print(data)
                    if data['found'] is True:
                        # print('RSSI:', data['rssi'])
                        return data

            if time.time() - start > timeout:
                return None

            time.sleep(0.1)

    def scanInit(self):
        ser = self.serial

        ser.flushInput()
        ser.flushOutput()

        # disconnect if we are connected already
        ble_cmd_connection_disconnect(ser, 0)
        response = ser.read(7) # 7-byte response

        # stop advertising if we are advertising already
        ble_cmd_gap_set_mode(ser, 0, 0)
        response = ser.read(6) # 6-byte response

        # stop scanning if we are scanning already
        ble_cmd_gap_end_procedure(ser)
        response = ser.read(6) # 6-byte response

        # set scan parameters
        ble_cmd_gap_set_scan_parameters(ser, 0xC8, 0xC8, False)
        response = ser.read(6) # 6-byte response

        # start scanning now
        # Note: In 'gap_discover_limited' (0) and 'gap_discover_generic' (1) modes
        # all 'non-conforming' (without 'flags' or with incorrect 'flags' value)
        # adverizing packets are silently discarded. All packets are visible in
        # 'gap_discover_observation' (2) mode. It is helpfull for debugging.
        ble_cmd_gap_discover(ser, 2)


def ble_scan():
    # global filter_uuid, filter_mac, filter_rssi

    # open serial port for BGAPI access
    try:
        ser = serial.Serial(port='COM12', baudrate=115200, timeout=1)
    except serial.SerialException as e:
        exit(2)

    # flush buffers
    ser.flushInput()
    ser.flushOutput()

    # disconnect if we are connected already
    ble_cmd_connection_disconnect(ser, 0)
    response = ser.read(7) # 7-byte response

    # stop advertising if we are advertising already
    ble_cmd_gap_set_mode(ser, 0, 0)
    response = ser.read(6) # 6-byte response

    # stop scanning if we are scanning already
    ble_cmd_gap_end_procedure(ser)
    response = ser.read(6) # 6-byte response

    # set scan parameters
    ble_cmd_gap_set_scan_parameters(ser, 0xC8, 0xC8, False)
    response = ser.read(6) # 6-byte response

    # start scanning now
    # Note: In 'gap_discover_limited' (0) and 'gap_discover_generic' (1) modes
    # all 'non-conforming' (without 'flags' or with incorrect 'flags' value)
    # adverizing packets are silently discarded. All packets are visible in
    # 'gap_discover_observation' (2) mode. It is helpfull for debugging.
    ble_cmd_gap_discover(ser, 2)

    while (1):
        # catch all incoming data
        while ser.inWaiting():
            # bgapi_parse(ord(ser.read()), 'TN 536881597')
            bgapi_parse(ord(ser.read()), '')

        # don't burden the CPU
        time.sleep(0.01)

# define API commands we might use for this script
def ble_cmd_system_reset(p, boot_in_dfu):
    p.write(struct.pack('5B', 0, 1, 0, 0, boot_in_dfu))

def ble_cmd_connection_disconnect(p, connection):
    p.write(struct.pack('5B', 0, 1, 3, 0, connection))

def ble_cmd_gap_set_mode(p, discover, connect):
    p.write(struct.pack('6B', 0, 2, 6, 1, discover, connect))

def ble_cmd_gap_end_procedure(p):
    p.write(struct.pack('4B', 0, 0, 6, 4))

def ble_cmd_gap_set_scan_parameters(p, scan_interval, scan_window, active):
    p.write(struct.pack('<4BHHB', 0, 5, 6, 7, scan_interval, scan_window, active))

def ble_cmd_gap_discover(p, mode):
    p.write(struct.pack('5B', 0, 1, 6, 2, mode))

# define basic BGAPI parser
bgapi_rx_buffer = []
bgapi_rx_expected_length = 0
def bgapi_parse(b, devicetofind):
    global bgapi_rx_buffer, bgapi_rx_expected_length
    if len(bgapi_rx_buffer) == 0 and (b == 0x00 or b == 0x80):
        bgapi_rx_buffer.append(b)
    elif len(bgapi_rx_buffer) == 1:
        bgapi_rx_buffer.append(b)
        bgapi_rx_expected_length = 4 + (bgapi_rx_buffer[0] & 0x07) + bgapi_rx_buffer[1]
    elif len(bgapi_rx_buffer) > 1:
        bgapi_rx_buffer.append(b)

    # print('buflen', len(bgapi_rx_buffer))
    # print('expected', bgapi_rx_expected_length)
    # if len(bgapi_rx_buffer) == 1000:
    #     print(bgapi_rx_buffer)
    #     sys.exit()

    #print '%02X: %d, %d' % (b, len(bgapi_rx_buffer), bgapi_rx_expected_length)
    if bgapi_rx_expected_length > 0 and len(bgapi_rx_buffer) == bgapi_rx_expected_length:
        #print '<=[ ' + ' '.join(['%02X' % b for b in bgapi_rx_buffer ]) + ' ]'
        packet_type, payload_length, packet_class, packet_command = bgapi_rx_buffer[:4]
        # print('x'*50)
        # print('asdasd', bgapi_rx_buffer)
        bgapi_rx_payload = bgapi_rx_buffer[4:]

        # print('PPPPP', bgapi_rx_payload)

        # print('qweqwe', type(bgapi_rx_payload), bgapi_rx_payload)
        # print('ZZZZRSSI', bgapi_rx_payload[0], bgapi_rx_payload[0])
        # if sys.version_info[0] == 3:
        #     bgapi_rx_payload = bgapi_rx_payload.encode()

        if packet_type & 0x80 == 0x00: # response
            bgapi_filler = 0
        else: # event
            if packet_class == 0x06: # gap
                if packet_command == 0x00: # scan_response
                    rssi, packet_type, sender, address_type, bond, data_len = struct.unpack('<bB6sBBB', bytes(bgapi_rx_payload[:11]))
                    sender = list(sender)
                    data_data = list(bgapi_rx_payload[11:])
                    # print('RSSI', bgapi_rx_payload[0])
                    # print('MMM rssi', rssi)
                    # print('MMM packet_type', packet_type)
                    # print('MMM sender', sender)
                    # print('MMM address_type', address_type)
                    # print('MMM bond', bond)
                    # print('MMM data_len', data_len)
                    # print('ddd', data_data, type(data_data))
                    display = 1

                    # parse all ad fields from ad packet
                    ad_fields = []
                    this_field = []
                    ad_flags = 0
                    ad_services = []
                    ad_local_name = []
                    ad_tx_power_level = 0
                    ad_manufacturer = []

                    bytes_left = 0
                    for b in data_data:
                        if bytes_left == 0:
                            bytes_left = b
                            this_field = []
                        else:
                            this_field.append(b)
                            bytes_left = bytes_left - 1
                            if bytes_left == 0:
                                ad_fields.append(this_field)
                                if this_field[0] == 0x01: # flags
                                    ad_flags = this_field[1]
                                if this_field[0] == 0x02 or this_field[0] == 0x03: # partial or complete list of 16-bit UUIDs
                                    for i in range( int((len(this_field) - 1) / 2)  ):
                                        ad_services.append(this_field[-1 - i*2 : -3 - i*2 : -1])
                                if this_field[0] == 0x04 or this_field[0] == 0x05: # partial or complete list of 32-bit UUIDs
                                    for i in range( int((len(this_field) - 1) / 4) ):
                                        ad_services.append(this_field[-1 - i*4 : -5 - i*4 : -1])
                                if this_field[0] == 0x06 or this_field[0] == 0x07: # partial or complete list of 128-bit UUIDs
                                    for i in range( int((len(this_field) - 1) / 16) ):
                                        ad_services.append(this_field[-1 - i*16 : -17 - i*16 : -1])
                                if this_field[0] == 0x08 or this_field[0] == 0x09: # shortened or complete local name
                                    ad_local_name = this_field[1:]
                                if this_field[0] == 0x0A: # TX power level
                                    ad_tx_power_level = this_field[1]

                                # OTHER AD PACKET TYPES NOT HANDLED YET

                                if this_field[0] == 0xFF: # manufactuerer specific data
                                    ad_manufacturer.append(this_field[1:])

                    if len(filter_mac) > 0:
                        match = 0
                        for mac in filter_mac:
                            if mac == sender[:-len(mac) - 1:-1]:
                                match = 1
                                break

                        if match == 0: display = 0

                    if display and len(filter_uuid) > 0:
                        if not [i for i in filter_uuid if i in ad_services]: display = 0

                    if display and filter_rssi > 0:
                        if -filter_rssi > rssi: display = 0

                    if display:
                        #print "gap_scan_response: rssi: %d, packet_type: %d, sender: %s, address_type: %d, bond: %d, data_len: %d" % \
                        #    (rssi, packet_type, ':'.join(['%02X' % ord(b) for b in sender[::-1]]), address_type, bond, data_len)
                        t = datetime.datetime.now()

                        disp_list = []
                        scandata = {}
                        for c in "trpsabd":
                            if c == 't':
                                dt = "%ld.%03ld" % (time.mktime(t.timetuple()), t.microsecond/1000)
                                disp_list.append(dt)
                                scandata['time'] = dt
                            elif c == 'r':
                                rssi = "%d" % rssi
                                disp_list.append(rssi)
                                scandata['rssi'] = rssi
                            elif c == 'p':
                                disp_list.append("%d" % packet_type)
                            elif c == 's':
                                sender = "%s" % ''.join(['%02X' % b for b in sender[::-1]])
                                disp_list.append(sender)
                                scandata['sender'] = sender
                            elif c == 'a':
                                disp_list.append("%d" % address_type)
                            elif c == 'b':
                                disp_list.append("%d" % bond)
                            elif c == 'd':
                                # disp_list.append("%s" % ''.join(['%02X' % b for b in data_data]))
                                dataline = ''
                                for b in data_data:
                                    c = chr(b)
                                    if c in ['\r', '\n']:
                                        continue
                                    if c in string.printable:
                                        dataline += c
                                if devicetofind in dataline or devicetofind == '':
                                    devfound = True
                                else:
                                    devfound = False
                                scandata['data'] = dataline
                                scandata['found'] = devfound

                                disp_list.append(dataline + '\t' + str(data_data))
                        if devfound:
                            print(' '.join(disp_list))
                            bgapi_rx_buffer = []
                            return scandata

        bgapi_rx_buffer = []
    return None

# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    #print 'Goodbye, cruel world!'
    exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    ble_scan()