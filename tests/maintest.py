'''
Created on 21 mei 2015

@author: e.schaeffer
updates
'''

from datetime import datetime
from pprint import pprint
import os
import sys
import time
import subprocess
import math
import numpy as np
import pygatt
import struct
import traceback
from base64 import b64decode

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = os.open(os.devnull, os.O_RDWR)

from UliEngineering.Physics.RTD import pt1000_temperature
from Instruments.PH_Instr_34970A import Instrument_34970A
from Instruments.SerialInterface import SerialInterface
from Instruments.Keysight_E36103A import Keysight_E36103A
import pyaudio
from settings.defines import *
from tests.settings_test import MSGOPTIONS
from module_locator import module_path

class TestFCTBold():
    toolreset_counter = 0
    msgflags = {}
    startfn = None
    clearfn = None

    def __init__(self, parent, hwsettings):
        self.parent = parent
        self.hwsettings = hwsettings
        self.settings = None

        self.startfn = self.relay_jigdown
        self.errorfn = self.errorHandler
        self.clearfn = self.relay_clrjig

        # list with methods for initialization
        self.instruments = [
            self.init_serial_dut,
            self.init_serial_led,
            self.init_gpib_dmm,
            self.init_psu,
            self.init_audio,
            self.init_ble,
            self.init_jlink,
            self.init_security
            ]

        self.tests = [
            self.check_settings,            # OK
            self.init_values,               # OK
            self.jig_sanity_check,          # OK

            self.psu_start,
            self.firmwareApplication,
            self.dut_start,
            self.dut_battery_voltage,
            self.dut_motor,
            self.dut_accelerometer,
            self.dut_magnetometer,
            self.dut_button,
            self.dut_buzzer,
            self.dut_leds,
            self.dut_standby,
            self.security,
            self.dut_ble_app,

            self.timedone,
            self.stamp,
            self.relay_clrjig,
        ]

        self.values = {}

    def failtest(self):
        return False

    def log_add(self, msg):
        self.parent.log_add(msg)

    def setError(self, message):
        self.log_addline(message)
        self.values['error'] = message.strip()

    def setValue(self, value, key, label=None, fmt=None):
        if label is None:
            label = key
        if fmt is None:
            fmt = '{:s}'
        self.log_addline('{:s}: {:.2f}'.format(label, value))

    def storeValue(self, key, value):
        self.values[key.lower()] = value

    def log_addline(self, msg):
        self.log_add(msg + '\n')

    def setTestSettings(self, settings):
        self.settings = settings

    def check_settings(self):
        self.time_start = time.time()
#         if self.settings is None:
#             self.log_add('No settings loaded')
#             return False
        return True

    def timedone(self):
        elapsed = time.time() - self.time_start
        self.log_addline('Test time: {:.1f}sec'.format(elapsed))
        return True

    def init_values(self):
        self.values = {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'testerid': self.hwsettings.general['testerid'],
            'testersw': title
        }

        if self.parent.parent.scannedBarcodeLine != '':
            self.values['qrcode'] = self.parent.parent.scannedBarcodeLine

        if not self.values['qrcode'].startswith(self.hwsettings.general['barcode_prefix']):
            self.setError('Invalid barcode prefix')
            return False

        try:
            deviceid = int(self.values['qrcode'][-6:])
        except:
            self.setError('Invalid barcode')
            return False

        if self.hwsettings.security['enabled'] is True:
            if deviceid not in self.security_keys:
                self.setError(f'key {deviceid} from barcode not available in security keys file')
                return False

        self.parent.logAddFilenamePrefix('FCT')
        self.parent.logAddFilenamePrefix(self.parent.barcode)

        return True

# INSTRUMENTS
    def init_psu(self):
        self.instrPSU = Keysight_E36103A()
        if self.instrPSU.connect_usb(self.hwsettings.psu['vid'],
                                     self.hwsettings.psu['pid']) is False:
            self.log_addline('  error connecting PSU')
            return False

        ret = self.instrPSU.Query('*IDN?')
        self.log_addline('  PSU init OK')
        self.log_addline('  PSU IDN: {:s}'.format(ret.strip()))

        self.instrPSU.Volt(0.0)
        self.instrPSU.Output_Off()

        return True

    def init_serial_dut(self):
        try :
            self.serDUT = SerialInterface(self.hwsettings.serial_dut['comport'],
                                          timeout=0.05,
                                          baudrate=115200,
                                          xonxoff=True,
                                          rtscts=False,
                                          dsrdtr=False
                                          )
        except:
            self.log_addline('  Serial DUT USB connection / Comport nr ERROR')
            return False
        self.log_addline('  Serial DUT init OK')
        return True

    def init_serial_led(self):
        self.log_add('  Serial LED Analyser  ')
        if self.hwsettings.serial_led['enabled'] is False:
            # led analyzer is disabled
            self.log_addline('skipped')
            return True
        try:
            self.serLed = SerialInterface(self.hwsettings.serial_led['comport'],
                                          timeout=0.05,
                                          baudrate=57600,
                                          xonxoff=True,
                                          rtscts=False,
                                          dsrdtr=False)
        except:
            self.log_addline('  USB connection / Comport nr ERROR')
            return False
        self.log_addline('init OK')
        return True

    def init_gpib_dmm(self):
        self.instrDMM = Instrument_34970A(addr=self.hwsettings.dmm['address'])
        if self.instrDMM.error is True:
            self.log_addline('  error connecting DMM')
            return False

        ret = self.instrDMM.Query('*IDN?')
        self.log_addline('  DMM init OK')
        self.log_addline('  DMM IDN: {:s}'.format(ret.strip()))

        self.Deactivate_Relay(Ry_Stamp)
        self.Deactivate_Relay(Ry_SerialEnable)
        self.Deactivate_Relay(Ry_Takeover)

        return True

    def init_jlink(self):
        if self.hwsettings.firmware['program_app'] is False:
            self.log_addline('  JLink - skipping (disabled)')
            return True

        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')

        try:
            ret = subprocess.check_output([nrfjexe, '--ids'], shell=True, stdin=DEVNULL, stderr=DEVNULL)
        except:
            self.log_addline('  JLink - executing nrfjprog error')
            self.log_addline(f'{nrfjexe}')
            traceback.print_exc()
            return False

        ret = ret.decode()
        ids = ret.split('\n')
        jlinkids = []
        for jlinkid in ids:
            if len(jlinkid) > 0:
                jlinkids.append(jlinkid.strip())

        if len(jlinkids) == 0:
            self.log_addline('  JLink Error: no devices found')
            return False

        if self.hwsettings.firmware['program_app']:
            hexfile = os.path.join(self.hwsettings.firmware['firmware_path'], self.hwsettings.firmware['hex_app'])
            if not os.path.isfile(hexfile):
                self.log_addline('  JLink - hex file {:s} not found'.format(hexfile))
                return False

        self.log_addline('  JLink OK (s/n:{:s})'.format(jlinkids[0]))

        return True

    def init_security(self):
        self.log_addline('  Security')
        if self.hwsettings.security['enabled'] is False:
            self.log_addline('    skipping (disabled')
            return True

        keysfile = self.hwsettings.security['keys_file']
        if not os.path.isfile(keysfile):
            self.log_addline(f'    keys file {keysfile} not found')
            return False

        self.security_keys = {}
        lines = open(keysfile, 'r').readlines()
        for line in lines:
            data = line.strip().split(',')
            try:
                deviceid = int(data[0])
            except:
                continue
            self.security_keys[deviceid] = data[1:]

        self.log_addline('    read {:d} keys from keys file {:s}'.format(len(self.security_keys), keysfile))

        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')

        try:
            ret = subprocess.check_output([nrfjexe, '--ids'], shell=True, stdin=DEVNULL, stderr=DEVNULL)
        except:
            self.log_addline('  JLink - nrfjprog error')
            return False

        ret = ret.decode()
        ids = ret.split('\n')
        jlinkids = []
        for jlinkid in ids:
            if len(jlinkid) > 0:
                jlinkids.append(jlinkid.strip())

        if len(jlinkids) == 0:
            self.log_addline('  JLink Error: no devices found')
            return False

        self.log_addline('    JLink OK (s/n:{:s})'.format(jlinkids[0]))

        return True


    def init_audio(self):
        self.log_add('  Audio/Microphone')
        if self.hwsettings.microphone['enabled'] is False:
            self.log_addline('  skipping (disabled')
            return True

        FORMAT = pyaudio.paInt16
        CHANNELS = 1

        try:
            self.paudio = pyaudio.PyAudio()
            self.audio_stream = self.paudio.open(format = FORMAT,
                                                 channels = CHANNELS,
                                                 rate = 44100,
                                                 input = True,
                                                 output = False,
                                                 frames_per_buffer = 1024)
        except:
            self.log_addline('  FAIL, error initializing audio/microphone')
            return False

        self.log_addline('  PASS')
        return True

    def init_ble(self):
        self.ble_dongle = pygatt.BGAPIBackend(serial_port='COM12')
        self.ble_dongle.start()
        return True

    def ble_find_device(self, devname):
        ADDRESS_TYPE = pygatt.BLEAddressType.random
        _devices = self.ble_dongle.scan(run_as_root=True, timeout=self.hwsettings.ble['scan_timeout'])

        UUID_DEVICE_NAME = '00002a00-0000-1000-8000-00805f9b34fb'

        devices = {}
        for dev in _devices:
            rssi = dev['rssi']
            if rssi > -50:
                devices[rssi] = dev

        for rssi in reversed(sorted(devices.keys())):
            device = devices[rssi]
            address = device['address']

            if device['rssi'] < -50:
                print('low rssi, skipping', address, device['rssi'])
                continue

            print('rssi, trying', address, device['rssi'])
            try:
                bledevice = self.ble_dongle.connect(address, address_type=ADDRESS_TYPE)
                try:
                    devicename = bledevice.char_read(UUID_DEVICE_NAME).decode()
                except:
                    continue
                print(devicename, device['rssi'])
                if devname in devicename:
                    return address, device['rssi']
                bledevice.disconnect()
            except pygatt.exceptions.NotConnectedError:
                # print("failed to connect to %s" % address)
                continue

        print('done')
        return False

    def ble_find_deviceid(self, address):
        devices = self.ble_dongle.scan(run_as_root=True, timeout=self.hwsettings.ble['scan_timeout'])

        for device in devices:
            if device['address'] != address:
                continue

            data = device['packet_data']['connectable_advertisement_packet']['manufacturer_specific_data']

            try:
                dd = struct.unpack('<HBBBQB', data)
            except:
                return False

            return dd[4]

        return False

    def ble_find_serialnr(self, serial):
        devices = self.ble_dongle.scan(run_as_root=True, timeout=self.hwsettings.ble['scan_timeout'])

        for device in devices:
            try:
                data = device['packet_data']['connectable_advertisement_packet']['manufacturer_specific_data']
                dd = struct.unpack('<HBBBQB', data)             
            except:
                continue

            # check manufacturer ID
            if dd[0] != 0x065B:
                continue

            # check serial nr
            if dd[4] == serial:
                return device['rssi']

        return False


    # when test exit perform nice instruments close (USB relay!)
    def closeInstruments(self):
        self.power_off()



# TESTS
    def psu_start(self):
        self.instrPSU.Volt(3.0)
        self.instrPSU.Amp(2.0)
        self.instrPSU.Output_On()

        self.log_addline('Switching PSU to 3.0V / 2.0A')

        currents = []
        for i in range(5):
            time.sleep(0.5)
            current = self.instrPSU.Measure_Amps() * 1000
            if i > 1:
                currents.append(current)

        current = sum(currents) / len(currents)

        voltage = self.instrDMM.Measure_Volt_DC('100', 6, '10', '5.5')

        self.log_add(f'  voltage: {voltage:.1f}V  ')
        if voltage < self.hwsettings.limits['startup_voltage_min']:
            self.setError('FAIL, voltage too low')
            return False
        self.log_addline('PASS')

        self.log_add(f'  current: {current:.1f}mA  ')
        if current > self.hwsettings.limits['startup_current_max']:
            self.setError('FAIL, current too high')
            return False
        self.log_addline('PASS')

        return True

    def dut_start(self):
        self.Activate_Relay(Ry_SerialEnable)

        # sys.exit(0)
        lines = self.dutQuery('')
        lines = self.dutQuery('get_firmware_version?')
        for line in lines:
            if line == '':
                continue
            try:
                version = int(line)
            except:
                self.setError('error parsing version number')
                return False

            self.log_add(f'DUT firmware version: {version}  ')
            if version != self.hwsettings.firmware['expected_version']:
                self.setError('FAIL, version mismatch')
                return False
            self.log_addline('PASS')
            self.dutQuery('disable_ble_advertising')
            return True
        return False

    def dut_battery_voltage(self):
        lines = self.dutQuery('read_battery_voltage?')  # dummy read
        lines = self.dutQuery('read_battery_voltage?')
        self.log_addline('battery voltage')
        battvoltage_fw = 0
        for line in lines:
            if line == '':
                continue

            try:
                battvoltage_fw = int(line)
            except:
                self.setError('error parsing battery voltage')
                return False

        battvoltage_dmm = self.instrDMM.Measure_Volt_DC('100', 6, '10', '4.5') * 1000

        self.log_addline(f'  firmware: {battvoltage_fw}mV')
        self.log_addline(f'  dmm:      {battvoltage_dmm:.0f}mV')
        if battvoltage_fw < self.hwsettings.limits['battery_voltage_fw_min']:
            self.setError('  FAIL, battery voltage too low')
            return False
        if battvoltage_fw > self.hwsettings.limits['battery_voltage_fw_max']:
            self.setError('  FAIL, battery voltage too high')
            return False

        return True

    def dut_motor(self):
        cmds = {
            'left': ('enable_motor_left', 0.5, 'neg', 1),
            'right': ('enable_motor_right', 0.5, 'pos', 1),
            'disable': ('disable_motor', 1.5, '-', 2)
        }

        results = {}
        for m, cmd_delay in cmds.items():
            cmd, delay, sign, retries = cmd_delay
            lines = self.dutQuery(cmd)
            motor_cmd_ok = False
            for line in lines:
                if line == '':
                    continue
                if line == 'OK':
                    motor_cmd_ok = True
                    break

            if motor_cmd_ok is False:
                self.setError(f'{cmd} FAIL')
                return False

            self.log_addline(f'{cmd} OK')

            for r in range(retries):
                error = False
                currenttry = r + 1
                time.sleep(delay)

                v = self.instrDMM.Measure_Volt_DC('100', 11, '10', '5.5')
                i = v / 25 * 1000
                ipsu = self.instrPSU.Measure_Amps()*1000
                self.log_addline(f'  voltage:     {v:.2f}V')
                self.log_add    (f'  current:     {i:.1f}mA    ')
                if sign == 'neg':
                    if i > 0:
                        error = True
                        self.setError('FAIL, wrong polarity')
                        if currenttry == retries:
                            return False
                if sign == 'pos':
                    if i < 0:
                        error = True
                        self.setError('FAIL, wrong polarity')
                        if currenttry == retries:
                            return False
                if m in ['left', 'right']:
                    if abs(i) < self.hwsettings.limits['motor_lr_current_min_abs']:
                        error = True
                        self.setError('FAIL, current too low')
                        if currenttry == retries:
                            return False
                if not error:
                    self.log_addline('PASS')

                self.log_add(f'  psu current: {ipsu:.1f}mA    ')
                if m in ['left', 'right']:
                    if ipsu < self.hwsettings.limits['motor_lr_psu_current_min']:
                        error = True
                        self.setError('FAIL, current too low')
                        if currenttry == retries:
                            return False
                elif m == 'disable':
                    if ipsu > self.hwsettings.limits['motor_disable_psu_current_max']:
                        error = True
                        self.setError('FAIL, current too high')
                        if currenttry == retries:
                            return False
                if not error:
                    self.log_addline('PASS')
                    break
                else:
                    self.log_addline('  retrying')

            results[m] = (v, i, ipsu)
            time.sleep(0.5)

        return True

    def dut_accelerometer(self):
        self.log_addline('accelerometer')
        lines = self.dutQuery('enable_power_accelerometer')
        line = ''.join(lines)
        time.sleep(0.5)

        voltage = self.instrDMM.Measure_Volt_DC('100', 12, '10', '5.5')
        self.log_add(f'  voltage: {voltage:.1f}V  ')
        if voltage < self.hwsettings.limits['accelero_voltage_on_min']:
            self.setError('FAIL, voltage too low')
            return False
        self.log_addline('PASS')

        lines = self.dutQuery('read_accelerometer?')
        line = ''.join(lines)
        values = line.split(',')

        vv = {}
        try:
            vv['x'] = int(values[0])
            vv['y'] = int(values[1])
            vv['z'] = int(values[2])
        except:
            self.setError('  FAIL, error reading values')
            return False

        if vv['x'] == vv['y'] and vv['x'] == vv['z']:
            for axis in ['x', 'y', 'z']:
                self.log_addline(f'  {axis}: {vv[axis]}  ')
            # all 3 values are the same, this is probably not correct
            self.setError('  FAIL, error all values are the same')
            return False

        result = True
        for axis in ['x', 'y', 'z']:
            self.log_add(f'  {axis}: {vv[axis]}  ')
            if vv[axis] < self.hwsettings.limits[f'accelero_{axis}_min']:
                self.setError('  FAIL, too low')
                result = False
            elif vv[axis] > self.hwsettings.limits[f'accelero_{axis}_max']:
                self.setError('  FAIL, too high')
                result = False
            else:
                self.log_addline('  PASS')

        lines = self.dutQuery('disable_power_accelerometer')
        line = ''.join(lines)

        return result

    def dut_magnetometer(self):
        self.log_addline('magnetometer')

        lines = self.dutQuery('enable_power_magnetometer')
        line = ''.join(lines)
        time.sleep(0.5)

        voltage = self.instrDMM.Measure_Volt_DC('100', 13, '10', '5.5')
        self.log_add(f'  voltage: {voltage:.1f}V  ')
        if voltage < self.hwsettings.limits['magneto_voltage_on_min']:
            self.setError('FAIL, voltage too low')
            return False
        self.log_addline('PASS')

        lines = self.dutQuery('read_magnetometer?')
        line = ''.join(lines)
        values = line.split(',')
        vv = {}
        try:
            vv['val1'] = int(values[0])
            vv['val2'] = int(values[1])
        except:
            self.setError('  FAIL, error reading values')
            return False

        result = True
        for v in ['val1', 'val2']:
            self.log_add(f'  {v}: {vv[v]}  ')
            if vv[v] < self.hwsettings.limits[f'magneto_{v}_min']:
                self.setError('  FAIL, too low')
                result = False
            elif vv[v] > self.hwsettings.limits[f'magneto_{v}_max']:
                self.setError('  FAIL, too high')
                result = False
            else:
                self.log_addline('  PASS')

        lines = self.dutQuery('disable_power_magnetometer')
        line = ''.join(lines)

        return result

    def dut_button(self):
        self.log_addline('button')
        lines = self.dutQuery('read_button?')
        line = ''.join(lines)
        self.log_add(f'  not pressed: {line}  ')
        if line != '0':
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        self.Activate_Relay(Ry_Button)
        time.sleep(self.hwsettings.button['activate_delay'])

        lines = self.dutQuery('read_button?')
        line = ''.join(lines)
        self.log_add(f'  pressed:     {line}  ')
        if line != '1':
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        self.Deactivate_Relay(Ry_Button)
        time.sleep(self.hwsettings.button['deactivate_delay'])

        lines = self.dutQuery('read_button?')
        line = ''.join(lines)
        self.log_add(f'  not pressed: {line}  ')
        if line != '0':
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        return True

    def audio_read(self, numsamples, label=None):
        if self.hwsettings.microphone['enabled'] is False:
            return 0
        data = self.audio_stream.read(numsamples)
        # PNE_DEBUG
        signal = np.fromstring(data, np.int16)
        # signal = np.fromstring(data, 'Int16')
        tot = sum(abs(x) for x in signal)
        tot = 20 * math.log10(tot)
        if label is not None:
            print(label, tot)
        return tot

    def dut_buzzer(self):
        self.log_addline('buzzer')
        _lines = self.dutQuery('enable_buzzer')
        time.sleep(0.2)
        dbon = self.audio_read(44100, 'ON')
        self.log_add(f'  on:    {dbon:.1f} dB  ')
        if dbon < self.hwsettings.limits['buzzer_min_level']:
            self.setError('FAIL, level too low')
            return False
        self.log_addline('PASS')

        time.sleep(0.5)

        _lines = self.dutQuery('disable_buzzer')
        self.audio_read(44100)
        self.audio_read(44100)
        dboff = self.audio_read(44100, 'OFF')
        self.log_addline(f'  off:   {dboff:.1f} dB')
        delta = dbon-dboff
        self.log_add(f'  delta: {delta:.1f} dB  ')
        if delta < self.hwsettings.limits['buzzer_delta_min']:
            self.setError('FAIL, delta too low')
            return False
        self.log_addline('PASS')

        return True

    def dut_standby(self):
        self.log_addline('standby')

        voltage = self.instrDMM.Measure_Volt_DC('100', 12, '10', '5.5')
        self.log_add(f'  accelero voltage: {voltage:.1f}V  ')
        if voltage > self.hwsettings.limits['accelero_voltage_off_max']:
            self.setError('FAIL, voltage too high')
            return False
        self.log_addline('PASS')

        voltage = self.instrDMM.Measure_Volt_DC('100', 13, '10', '5.5')
        self.log_add(f'  magneto voltage: {voltage:.1f}V  ')
        if voltage > self.hwsettings.limits['magneto_voltage_off_max']:
            self.setError('FAIL, voltage too high')
            return False
        self.log_addline('PASS')

        _lines = self.dutQuery('enter_standby')
        self.Deactivate_Relay(Ry_SerialEnable)
        time.sleep(1)

        ipsu = self.instrPSU.Measure_Amps()
        self.log_addline(f'  psu current:     {ipsu*1_000_000:.1f}uA')
        if ipsu > 0.3e-3:
            self.setError('  standby psu current too high')
            return False

        self.Activate_Relay(Ry_10kResistor)
        time.sleep(0.5)

        vv = []
        for _i in range(4):
            v = self.instrDMM.Measure_Volt_DC('100', 16, '0.1', '4.5')
            time.sleep(0.5)
            vv.append(v)

        v = sum(vv) / len(vv)
        standby_current = v *1_000_000/10_000
        self.log_add(f'  standby current: {standby_current:.1f}uA  ')
        if standby_current > self.hwsettings.limits['standby_current_max']:
            self.setError('FAIL, standby current too high')
            return False
        self.log_addline('PASS')

        self.Deactivate_Relay(Ry_10kResistor)
        return True

    def dut_leds(self):
        if self.hwsettings.ledtest['analyzer_enable'] is False:
            return True
        cmds = {
            'red': 'enable_red_led',
            'green': 'enable_green_led',
            'blue': 'enable_blue_led'
        }

        self.log_addline('LEDs')
        for color, cmd in cmds.items():
            self.dutQuery(cmd)
            time.sleep(.25)
            leds = self.ledAnalyse([1,2])
            self.log_addline(f'  {color}')
            for ch in [1,2]:
                try:
                    cr = leds[ch]['red']
                    cg = leds[ch]['green']
                    cb = leds[ch]['blue']
                    ci = leds[ch]['intensity']
                except:
                    self.setError('FAIL, error reading led analyzer')
                    return False
                self.log_add(f'     {ch}: {cr:03d}, {cg:03d}, {cb:03d}, {ci}  ')
                if color == 'red':
                    if cr < self.hwsettings.ledtest['red_min']:
                        self.setError('FAIL, red too low')
                        return False
                    if cg > self.hwsettings.ledtest['color_off_max']:
                        self.setError('FAIL, green too high')
                        return False
                    if cb > self.hwsettings.ledtest['color_off_max']:
                        self.setError('FAIL, blue too high')
                        return False
                elif color == 'green':
                    if cg < self.hwsettings.ledtest['green_min']:
                        self.setError('FAIL, green too low')
                        return False
                    if cr > self.hwsettings.ledtest['color_off_max']:
                        self.setError('FAIL, red too high')
                        return False
                    if cb > self.hwsettings.ledtest['color_off_max']:
                        self.setError('FAIL, blue too high')
                        return False
                elif color == 'blue':
                    if cb < self.hwsettings.ledtest['blue_min']:
                        self.setError('FAIL, blue too low')
                        return False
                    if cg > self.hwsettings.ledtest['color_off_max']:
                        self.setError('FAIL, green too high')
                        return False
                    if cr > self.hwsettings.ledtest['color_off_max']:
                        self.setError('FAIL, red too high')
                        return False
                if ci < self.hwsettings.ledtest['intensity_min']:
                    self.setError('FAIL, intensity too low')
                    return False
                if ci > self.hwsettings.ledtest['intensity_max']:
                    self.setError('FAIL, intensity too high')
                    return False
                self.log_addline('PASS')

            self.dutQuery('disable_leds')
            time.sleep(.25)

        return True

    def dut_ble(self):
        self.log_addline('BLE')

        self.dutQuery('enable_ble_advertising')
        time.sleep(0.5)

        self.log_add('  searching for "Bold lock" beacon')

        for _i in range(2):
            ret = self.ble_find_device('Bold')
            if ret is not False:
                break

        if ret is False:
            self.setError('  FAIL, device not found')
            return False

        self.log_addline('  PASS')

        self.ble_address, rssi = ret
        self.log_addline(f'  address: {self.ble_address}')
        self.log_addline(f'  RSSI:    {rssi}dBm')

        _lines = self.dutQuery('disable_ble_advertising')
        return True

    def dut_ble_app(self):
        self.log_addline('BLE application advertising')
        if self.hwsettings.security['enabled'] is False:
            self.log_addline('    skipping (disabled')
            return True

        for _i in range(self.hwsettings.ble['retries']):
            rssi = self.ble_find_serialnr(self.ble_deviceid)
            if rssi is False:
                self.log_addline('  device not found, retrying')
                continue

            self.log_addline(f'  address {self.ble_deviceid} found')
            self.log_addline(f'  manufacturer id found')
            self.log_add(f'  RSSI: {rssi}  ')
            if rssi < self.hwsettings.ble['rssi_min']:
                self.log_addline('  RSSI too low, retrying')
                continue
            break

        if rssi is False:
            self.setError('  FAIL, BLE device not found')
            return False

        if rssi < self.hwsettings.ble['rssi_min']:
            self.setError('FAIL, RSSI too low')

            ret = self.firmwareErase()
            self.log_add('    erasing device... ')
            if ret:
                self.log_addline('device erased')
            else:
                self.log_addline('failed to erase device')

            return False
        self.log_addline('PASS')

        return True

    def power_off(self):
        self.instrPSU.Output_Off()
        self.Deactivate_Relay(Ry_Stamp)
        self.Deactivate_Relay(Ry_SerialEnable)
        self.Deactivate_Relay(Ry_10kResistor)
        self.Deactivate_Relay(Ry_Button)
        self.Activate_Relay(Ry_Jlink)

        return True

    def jig_sanity_check(self, skipecho=False):
        value = self.instrDMM.Measure_Volt_DC('100', 18, '100', resolution = '5.5')
        self.log_addline('jig 24V: {:.1f}V'.format(value))
        self.storeValue('jig24v', value)
        if value < 20.0:
            self.setError('jig 24V FAIL')
            return False

        value = self.instrDMM.Measure_Ohm('100', 20)
        self.jigtemp = pt1000_temperature(value)
        self.log_addline('jig temperature: {:.1f}degC'.format(self.jigtemp))
        self.storeValue('jigtemp', self.jigtemp)

        self.Deactivate_Relay(Ry_Stamp)
        self.Deactivate_Relay(Ry_SerialEnable)
        self.Activate_Relay(Ry_Jlink)

        return True

    def firmwareApplication(self):
        self.log_addline('Programming application firmware    ')
        if self.hwsettings.firmware['program_app'] is False:
            self.log_addline('  skipped')
            return True

        self.Deactivate_Relay(Ry_Jlink)

        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')

        hexfile = os.path.join(self.hwsettings.firmware['firmware_path'], self.hwsettings.firmware['hex_app'])

        if not os.path.exists(hexfile):
            self.setError('hexfile {:s} does not exist'.format(hexfile))
            return False

        self.log_add('  unlocking    ')
        try:
            _ret = subprocess.run([nrfjexe, '-f', 'NRF52', '--recover'], shell=True, check=True)
        except:
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        self.log_add('  programming {:s}    '.format(self.hwsettings.firmware['hex_app']))
        try:
            _ret = subprocess.run([nrfjexe, '-f', 'NRF52', '--program', hexfile, '--chiperase', '--verify' ],
                                  shell=True,
                                  check=True)
        except:
            self.setError('FAIL')
            return False

        self.log_addline('PASS')

        time.sleep(0.5)

        try:
            # PNE_DEBUG
            self.log_addline("Power-ON Reset")
            self.instrPSU.Output_Off()
            time.sleep(0.5)
            self.instrPSU.Output_On()
            time.sleep(0.5)
            # PNE_DEBUG

            # _ret = subprocess.run([nrfjexe, '-f', 'NRF52', '--reset'],
            #                       shell=True,
            #                       check=True)
        except:
            self.log_addline('  reset processor FAIL')
            return False                

        self.Activate_Relay(Ry_Jlink)

        self.log_addline('  reset processor PASS')
        time.sleep(0.5)

        return True

    def firmwareErase(self):
        self.Deactivate_Relay(Ry_Jlink)

        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')

        try:
            _ret = subprocess.run([nrfjexe, '-f', 'NRF52', '--recover'], shell=True, check=True)
        except:
            return False
        return True

    def debugexit(self):
        self.Activate_Relay(Ry_SerialEnable)
        time.sleep(1)
        sys.exit()

    def dutQuery(self, cmd, timeout=None, findstr=None):
        self.serDUT.write(cmd+'\r')
        if timeout is None:
            ret = self.serDUT._readlines(findstr=findstr)
        else:
            ret = self.serDUT._readlines(timeout=timeout,
                                         findstr=findstr)
        lines = ret.split('\n')
        output = []
        for line in lines:
            output.append(line.strip())
        return output

    def ledAnalyse(self, channels):
        if self.hwsettings.ledtest['analyzer_enable'] is False:
            return True

        _start = time.time()
        brightness_level = self.hwsettings.ledtest['brightness_level']
        if brightness_level in [1,2,3,4,5]:
            self.serLed.write('C{:d}\r\n'.format(brightness_level))
        else:
            self.serLed.write('C\r\n')

        ret = self.serLed._readlines(timeout=0.5, findstr='OK')

        leds = {}
        for channel in channels:
            self.serLed.write('getrgbi{:02d}\r\n'.format(channel))
            ret = self.serLed.readlines()

            lines = ''
            for line in ret:
                lines += line.decode()

            # print(channel, lines)
            lines = lines.split('\n')
            led = {}
            for line in lines:
                if line == '':
                    continue

                items = line.strip().split(' ')

                try:
                    led = {
                        'red': int(items[0]),
                        'green': int(items[1]),
                        'blue': int(items[2]),
                        'intensity': int(items[3])
                    }
                except:
                    continue
            leds[channel] = led

        _end = time.time()
#         print('elapsed getall', end-start)
        return leds
    
    def security_program_address(self, address, value):
        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')

        if not value.startswith('0x'):
            value = '0x' + value

        try:           
            _ret = subprocess.run([nrfjexe, '--memwr', address, '--val', value], shell=True, check=True)
        except:
            return False
        return True

    def security(self):
        # PNE_DEBUG
        self.log_addline('Programming application firmware    ')
        if self.hwsettings.firmware['program_app'] is False:
            self.log_addline('  skipped')
            return True
    
        self.Deactivate_Relay(Ry_Jlink)

        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')

        hexfile = os.path.join(self.hwsettings.firmware['firmware_path'], self.hwsettings.firmware['hex_app'])

        if not os.path.exists(hexfile):
            self.setError('hexfile {:s} does not exist'.format(hexfile))
            return False

        self.log_add('  unlocking    ')
        try:
            _ret = subprocess.run([nrfjexe, '-f', 'NRF52', '--recover'], shell=True, check=True)
        except:
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        self.log_add('  programming {:s}    '.format(self.hwsettings.firmware['hex_app']))
        try:
            _ret = subprocess.run([nrfjexe, '-f', 'NRF52', '--program', hexfile, '--chiperase', '--verify' ],
                                  shell=True,
                                  check=True)
        except:
            self.setError('FAIL')
            return False

        self.log_addline('PASS')

        time.sleep(0.5)

        # PNE_DEBUG

        self.log_addline('Security')
        if self.hwsettings.security['enabled'] is False:
            self.log_addline('  skipping (disabled')
            return True

        self.Deactivate_Relay(Ry_Jlink)

        self.log_add(f'  model and type: {self.hwsettings.security["model_and_type"]}    ')
        if self.security_program_address('0x10001080', self.hwsettings.security["model_and_type"]) is False:
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        deviceid = int(self.values['qrcode'][-6:])

        self.log_add(f'  device id:      0x{deviceid:016X} ({deviceid})    ')
        ret1 = self.security_program_address('0x10001088', f'{deviceid:016X}'[8:16])
        ret2 = self.security_program_address('0x1000108C', f'{deviceid:016X}'[0:8])
        if ret1 is False or ret2 is False:
            self.setError('FAIL')
            return False
        self.log_addline('PASS')
        self.ble_deviceid = deviceid

        addresses = {
            0: ('0x10001090', '0x10001094', '0x10001098', '0x1000109C'),
            1: ('0x100010A0', '0x100010A4', '0x100010A8', '0x100010AC'),
            2: ('0x100010B0', '0x100010B4', '0x100010B8', '0x100010BC'),
            3: ('0x100010C0', '0x100010C4', '0x100010C8', '0x100010CC')
        }

        keys = []
        for i in range(4):
            key = list(b64decode(self.security_keys[deviceid][i]))
            key.reverse()
            key = bytes(key).hex()
            keys.append(key)

        for i, key in enumerate(keys):
            self.log_add(f'  key {i+1}:      ')
            ret1 = self.security_program_address(addresses[i][0], keys[i][24:32])
            ret2 = self.security_program_address(addresses[i][1], keys[i][16:24])
            ret3 = self.security_program_address(addresses[i][2], keys[i][8:16])
            ret4 = self.security_program_address(addresses[i][3], keys[i][0:8])
            if False in [ret1, ret2, ret3, ret4]:
                self.setError('FAIL')
                return False
            self.log_addline('PASS')

        self.log_add('  enable readback protection    ')
        nrfjprogpath = self.hwsettings.firmware['nrfjprog_path']
        nrfjexe = os.path.join(nrfjprogpath, 'nrfjprog.exe')
        try:
            _ret = subprocess.run([nrfjexe, '--rbp', 'ALL'], shell=True, check=True)
        except:
            self.setError('FAIL')
            return False
        self.log_addline('PASS')

        return True


    def stamp(self):
        self.Activate_Relay(Ry_Stamp)
        time.sleep(self.hwsettings.general['stamp_delay'])
        self.Deactivate_Relay(Ry_Stamp)
        return True


    def message(self):
        flag = False
        message = ''
        for msg in self.settings.messages:
            for opt in MSGOPTIONS:
                if msg[opt] is not None:
                    if msg[opt] in self.msgflags[opt]:
                        flag = True
                    else:
                        flag = False
            if flag:
                message = msg['message']
                break

        if flag:
            self.parent.action_update(message, 0)
            pass


    # take over the pneumatic valve, keep jig down
    def relay_jigdown(self):
        return False

    def relay_setjig(self):
        return True

    def relay_clrjig(self):
        self.power_off()
        return True

    def errorHandler(self):
        return True

    def Activate_Relay(self, port=(200,2,0)):
        self.instrDMM.A34907A_Digital_Output_bit(str(port[0]),port[1],port[2],True)

    def Deactivate_Relay(self, port=(200,2,0)):
        self.instrDMM.A34907A_Digital_Output_bit(str(port[0]),port[1],port[2],False)
