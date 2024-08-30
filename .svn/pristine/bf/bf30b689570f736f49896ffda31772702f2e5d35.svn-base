'''
Created on 6 mrt. 2014

@author: e.schaeffer
'''

from visa import *      # high level functions
from pyvisa import *    # low level functions vpp43

import time
import sys

# the Yokogawa WT310 power meter
class Instrument_WT310_donotuse:
    handle = None

    def __init__(self):
        self.handle = None

    def find_usb_instrument(self, vid, pid):
        try:
            instruments = visa.get_instruments_list()
        except:
            return None

        for instr in instruments:
            if 'USB' in instr:
                if str(vid) in instr and str(pid) in instr:
                    return instr
        return None

    # check for proper USB instrument connected and set handle
    def connect_usb(self, vid, pid):
        instr = self.find_usb_instrument(vid, pid)

        if instr is not None:
            try:
                self.handle = visa.Instrument(instr)
            except:
                print 'Error connecting camera'
                return False
        else:
            print 'ERROR, no USB instruments found'
            return False

        self.init_instrument()
        return True

    def init_instrument(self):
        self.handle.write('*RST\n')
        self.handle.write('*CLS\n')                   # clear previous errors
        self.handle.write('SAMPLE:HOLD OFF\n')        # hold off, instrument is sampling
        self.handle.write('MODE RMS\n')               # mode RMS for V/A
#         self.handle.write('FILTER OFF\n')             # freq.meas low pass filter OFF
#         self.handle.write('lFILTER OFF\n')            # V/A low pass filter OFF
        self.handle.write('SCALING OFF; AVERAGING OFF\n') # no scaling, no averaging
        self.handle.write('VOLTAGE:RANGE 300V\n')      # 300V
        self.handle.write('CURRENT:RANGE 5A\n')       # 5A
        self.handle.write('MEASURE:ITEM:PRESET NORMAL\n') # V-A-W are the defaults to measure
        self.handle.write('STATUS:FILTER1 FALL\n')    # configure EESR bit 0 == 1 after data update
        self.handle.write('STATUS:EESR?\n')           # dummy read EESR, clear all status bits
#         dummy = self.handle.read()                  # actual read EESR

    # set current range
    def Set_Range_Amp(self, amp = '20A'):
        if amp not in ['10A', '5A', '2A', '1A', '500mA', '200mA', '100mA', '50mA', '20mA', '5mA']:
            return False

        self.handle.write('CONF:CURR:RANGE {:s}\n'.format(amp))
        return True

    # set Voltage range
    def Set_Range_Volt(self, volt = '600V'):
        if volt not in ['600V', '300V', '150V', '60V', '30V', '15V']:
            return False

        self.handle.write('CONF:VOLT:RANGE {:s}\n'.format(volt))
        return True

    # prepare the instrument to sample new data
    # instrument is continuously sampling, clear EESR data update bit
    # and wait for new data available
    # here after retrieve data with "MEAS:NORM:VALUE?
    def Sample_New_Data(self):
        self.handle.write('STATUS:EESR?\n')               # dummy read EESR, clear all status bits
#         dummy = self.handle.read()                      # actual read EESR

        self.handle.write('COMM:WAIT 1\n')                # wait for NEW taken
        self.handle.write('STATUS:EESR?\n')               # dummy read EESR, clear all status bits
#         dummy = self.handle.read()                      # actual read EESR


    # return tuple with V,A,W
    def Get_VAW(self):
        # get NEW data sample
        self.Sample_New_Data()

        # retrieve this new data
        self.handle.write('MEAS:NORM:VALUE? \n')
        # read max 40 bytes from instrument
        response = self.handle.read()

        # convert the low A and W to mA and mW
        self.wt310_Volt = float(response.split(',')[0])
        self.wt310_Amp  = float(response.split(',')[1])
        self.wt310_Watt = float(response.split(',')[2])
        return (self.wt310_Volt, self.wt310_Amp, self.wt310_Watt)

    # float Volt
    def Get_Volt(self):
        # get Volt / Amp / Watt
        temp = self.Get_VAW()
        return temp[0]

    # float Amp
    def Get_Amp(self):
        # get Volt / Amp / Watt
        temp = self.Get_VAW()
        return temp[1]

    # float Watt
    def Get_Watt(self):
        # get Volt / Amp / Watt
        temp = self.Get_VAW()
        return temp[2]



# the Yokogawa WT210 power meter
class Instrument_WT210:
    wt210_handle = None
    # constructor, open and init gpib channel, init inistrument
    def __init__(self, board = 0, addr = 1):
        # define / init Yokogawa Wattmeter
#        self.wt210_handle = instrument('GPIB%s::%s'%(board,addr))
        self.visa_handle = vpp43.open_default_resource_manager()

        # open handle to instrument
        self.wt210_handle = vpp43.open(self.visa_handle,'GPIB'+str(board)+'::'+str(addr),VI_NULL,VI_NULL)

        vpp43.clear(self.wt210_handle)                          # Selective Device Clear (SDC)

        # settings to instrument
        vpp43.write(self.wt210_handle,'*RST')                   # reset instrument
        vpp43.write(self.wt210_handle,'*CLS')                   # clear previous errors
        vpp43.write(self.wt210_handle,'SAMPLE:HOLD OFF')        # hold off, instrument is sampling
        vpp43.write(self.wt210_handle,'MODE RMS')               # mode RMS for V/A
        vpp43.write(self.wt210_handle,'FILTER OFF')             # freq.meas low pass filter OFF
        vpp43.write(self.wt210_handle,'lFILTER OFF')            # V/A low pass filter OFF
        vpp43.write(self.wt210_handle,'SCALING OFF; AVERAGING OFF') # no scaling, no averaging
        vpp43.write(self.wt210_handle,'VOLTAGE:RANGE 300')      # 300V
        vpp43.write(self.wt210_handle,'CURRENT:RANGE 5A')       # 5A
        vpp43.write(self.wt210_handle,'MEASURE:ITEM:PRESET NORMAL') # V-A-W are the defaults to measure
        vpp43.write(self.wt210_handle,'STATUS:FILTER1 FALL')    # configure EESR bit 0 == 1 after data update
        vpp43.write(self.wt210_handle,'STATUS:EESR?')           # dummy read EESR, clear all status bits
        dummy = vpp43.read(self.wt210_handle,40)                # actual read EESR

    # set current range in mA steps
    # 5-10-20-50-100-200-500-1000-2000-5000-10000-20000
    def Set_Range_Amp(self, amp = 20000):
        if amp == 10000:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 10A')
        elif amp == 5000:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 5A')
        elif amp == 2000:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 2A')
        elif amp == 1000:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 1A')
        elif amp == 500:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 500mA')
        elif amp == 200:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 200mA')
        elif amp == 100:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 100mA')
        elif amp == 50:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 50mA')
        elif amp == 20:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 20mA')
        elif amp == 10:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 10mA')
        elif amp == 5:
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 5mA')
        else :
            vpp43.write(self.wt210_handle,'CONF:CURR:RANGE 20A')

    # return Standard Event Register (ESR) RO
    def Get_ESR(self):
        vpp43.write(self.wt210_handle,'*ESR?')
        return int(self.wt210_handle.read())

    # set Standard Event Enable Register (ESE) WO
    def Set_ESE(self, data = 0x00):
        vpp43.write(self.wt210_handle,'*ESE = %d'%data)

    # return Status Byte (STB) RO
    def Get_STB(self):
        stat = vpp43.read_stb(self.wt210_handle)
        return int(stat)

    # set Service Request Enable Register (SRE)
    def Set_SRE(self, data = 0x00):
        vpp43.write(self.wt210_handle,'*SRE = %d'%data)

    # return Service request Enable register (SRE)
    def Get_SRE(self):
        vpp43.write(self.wt210_handle,'*SRE?')
        return int(vpp43.read(self.wt210_handle,40))

    # return Condition Register
    def Get_Condition(self):
        vpp43.write(self.wt210_handle,'STAT:COND?')
        return int(vpp43.read(self.wt210_handle,40))


    # return Extended Event Status Register (EESR)
    def Get_EESR(self):
        vpp43.write(self.wt210_handle,'STAT:EESR?')
        return int(vpp43.read(self.wt210_handle,40))

    # return Error String
    def Get_ERROR(self):
        vpp43.write(self.wt210_handle,'STAT:EESR?')
        return vpp43.read(self.wt210_handle,40)

    # prepare the instrument to sample new data
    # instrument is continuously sampling, clear EESR data update bit
    # and wait for new data available
    # here after retrieve data with "MEAS:NORM:VALUE?
    def Sample_New_Data(self):
        vpp43.write(self.wt210_handle,'STATUS:EESR?')   # dummy read EESR, clear all status bits
        dummy = vpp43.read(self.wt210_handle,40)        # actual read EESR
#        print 'EESR before COMM:WAIT 1 = %02x'%int(dummy)
        vpp43.write(self.wt210_handle,'COMM:WAIT 1')    # wait for NEW taken
        vpp43.write(self.wt210_handle,'STATUS:EESR?')   # dummy read EESR, clear all status bits
        dummy = vpp43.read(self.wt210_handle,40)        # actual read EESR
#        print 'EESR after COMM:WAIT 1 = %02x'%int(dummy)

    # STB and error printing
    def Print_STB_Contents(self):
        stb = self.Get_STB()
        if stb & 0x04 != 0x00 :
            print 'STB EAV => Error Available'
        if stb & 0x08 != 0x00 :
            print 'STB EES => Extended Event Summary bit'
        if stb & 0x10 != 0x00 :
            print 'STB MAV => message available'
        if stb & 0x20 != 0x00 :
            print 'STB ESB => Event Summary Bit'
        if stb & 0x40 != 0x00 :
            print 'STB RQS/MMS => Request for Service / Master Summary Status'

    def Check_For_Error(self):
        if self.Get_STB() & 0x04 != 0x00 :
            vpp43.write(self.wt210_handle,'STATUS:ERROR?')
            print 'Error : %s'%vpp43.read(self.wt210_handle,40)

    # set Voltage range in V steps
    # 5-10-20-50-100-200-500-1000-2000-5000-10000-20000
    def Set_Range_Volt(self, volt = 600):
        print('handle', self.wt210_handle)
        if volt == 300:
            vpp43.write(self.wt210_handle,'CONF:VOLT:RANGE 300V')
        elif volt == 150:
            vpp43.write(self.wt210_handle,'CONF:VOLT:RANGE 150V')
        elif volt == 60:
            vpp43.write(self.wt210_handle,'CONF:VOLT:RANGE 60V')
        elif volt == 30:
            vpp43.write(self.wt210_handle,'CONF:VOLT:RANGE 30V')
        elif volt == 15:
            vpp43.write(self.wt210_handle,'CONF:VOLT:RANGE 15V')
        else :
            vpp43.write(self.wt210_handle,'CONF:VOLT:RANGE 600V')


    # return tuple with V,A,W
    def Get_VAW(self):
        # get NEW data sample
        self.Sample_New_Data()
        # retrieve this new data
        vpp43.write(self.wt210_handle,'MEAS:NORM:VALUE? ')
        # read max 40 bytes from instrument
        self.wt210_response = vpp43.read(self.wt210_handle,80)
        # convert the low A and W to mA and mW
        self.wt210_Volt = float(self.wt210_response.split(',')[0])
        self.wt210_Amp  = float(self.wt210_response.split(',')[1])
        self.wt210_Watt = float(self.wt210_response.split(',')[2])
        return (self.wt210_Volt, self.wt210_Amp, self.wt210_Watt)

    # float Volt
    def Get_Volt(self):
        # get Volt / Amp / Watt
        temp = self.Get_VAW()
        return temp[0]

    # float Amp
    def Get_Amp(self):
        # get Volt / Amp / Watt
        temp = self.Get_VAW()
        return temp[1]

    # float Watt
    def Get_Watt(self):
        # get Volt / Amp / Watt
        temp = self.Get_VAW()
        return temp[2]


def testwt210():
#     power_meter = Instrument_WT210(0,1)
#
#
#     power_meter.Set_Range_Volt(300)     # 300V range
#     power_meter.Set_Range_Amp(100)      # 100mA
#
#
# #     print '\n========================================================================================\n'
# #
# #     while True :
# #         print '--------------------------------------------------------------------'
# #         print '                 Start SunAmp functional test'
# #         print '--------------------------------------------------------------------\n\n'
# #
# #         print 'Q Enter to quit, Enter to perform SunAmp Test'
# #         user = raw_input()
# #         if user == 'Q' or user == 'q' :
# #             print 'End of test\n\n\n\n'
# #             break
# #         pcb_fail = False
# #         while True :
# # Switch ON the 230V to the SunAmp
# #     print '*** Switching ON the 230V mains ***'
# # measure mains Voltage
#     mains_voltage = power_meter.Get_Volt()
#     print 'Mains Voltage       ==> %3.2f Volt ..........'%mains_voltage,       # , as last object remove \n
#     if (mains_voltage > 215) and (mains_voltage < 245) :
#         print 'OK'
#     else :
#         pcb_fail = True
# #        break
# # measure mains standby power
#     power_meter.Set_Range_Amp(50)      # 20mA
#     mains_standby_power = power_meter.Get_Watt()
#     print 'Mains Standby Power ==>   %3.2f Watt ..........'%mains_standby_power,  # , as last object remove \n
# #     if (mains_standby_power > 1.2) and (mains_standby_power < 1.75) :
# #         print 'OK'
# #     else :
# #         pcb_fail = True
# #         break
#
#     power_meter.Set_Range_Amp(100)      # 100mA
    pass

if __name__ == '__main__' :
    powermeter = Instrument_WT310()
    powermeter.connect_usb('0x0B21', '0x0025')

    print powermeter.Set_Range_Volt('300V')     # 300V range
    print powermeter.Set_Range_Amp('100mA')     # 100mA
    print(powermeter.Get_VAW())
