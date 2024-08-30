#!/usr/local/bin/python
#
# low level commands for Keithley 2306
#    Battery Charger / Simulator
#
# powersupply 0-15V/7A or 0-30V/4A
# PdV 16-10-2014 check *IDN? for real 2306 instrument
# PdV 01-02-2014

import visa
import time
import sys

OUTPUT_BATTERY = 1
OUTPUT_CHARGE  = 2

class Instrument_2306:
    # constructor, open and init gpib channel, init instrument

    def __init__(self, board = 0, addr = 5):
        try :
            rm = visa.ResourceManager()
            res = rm.list_resources()
            self.handle = rm.open_resource('GPIB{:d}::{:d}::INSTR'.format(board, addr))

            # instrument in FactoryReset state , reset status bits
            self.handle.write('*RST ; *CLS')
            self.error = False
        except visa.VisaIOError :
            print ('Error instrument 34970A GPIB address')
            self.error = True
            return

#        # check if this is a real 2306
        idn_response = self.Query('*IDN?')
        if not '2306' in idn_response :
            print >> sys.stderr, 'Error instrument 2306 *IDN?'
            self.error = True
            return
        self.handle.write('BOTHOUTOFF')         # both outputs off
        self.handle.write('SOUR1:VOLT 0.0')     # output voltage 0.0
        self.handle.write('SOUR2:VOLT 0.0')     # for both supplies
        self.handle.write('SENS1:CURR:RANG:AUTO 1') # auto range I 1
        self.handle.write('SENS2:CURR:RANG:AUTO 1') # auto range I 2
        self.error = False
        self.high_range = False


    # send command to instrument
    # read response
    def Query(self,command = '*IDN?'):
        self.handle.write(command)
        time.sleep(0.1)     # recovery time
        return self.handle.read()


    # reset all channels to 'OPEN'
    def Reset(self):
        self.handle.write('*RST')                   # reset instrument all switches 'OPEN'
        self.handle.write('*CLS')                   # reset errors

    # switch ON / OFF the selected output
    def Output_On(self,supply = 1, out_on=False):
        if supply not in [OUTPUT_BATTERY, OUTPUT_CHARGE]:
            print('Error 2306 supply number either 1 or 2 {:d}'.format(supply))

        else :
            if out_on : # selected supply ON
                if supply == OUTPUT_BATTERY:
                    self.handle.write('OUTP1:STATE ON')
                else :
                    self.handle.write('OUTP2:STATE ON')
            else : # selected supply OFF
                if supply == OUTPUT_BATTERY:
                    self.handle.write('OUTP1:STATE OFF')
                else :
                    self.handle.write('OUTP2:STATE OFF')


    # set the output voltage
    def Volt(self,supply = 1, volts = 0.0):
        if supply not in [1, 2]:
            print('Error 2306 supply number either 1 or 2 {:d}'.format(supply))
        else :
            if volts <= 15.0 :
                if supply == 1 :
                    line = 'SOUR1:VOLT %2.3f'%volts
                else :
                    line = 'SOUR2:VOLT %2.3f'%volts
                self.handle.write(line)
            else :
                print ('2306 Voltage out of range %2.3f'%volts)


    # set the max output current
    def Amp(self,supply = 1, amps = 0):
        if supply not in [1, 2]:
            print >> sys.stderr,'Error 2306 supply number either 1 or 2 %d'%supply
        else :
            if  amps <= 5.0 :
                if supply == 1 :
                    self.handle.write('SOUR1:CURR %2.3f'%amps)
                else :
                    self.handle.write('SOUR2:CURR %2.3f'%amps)
            else :
                print >> sys.stderr,'2306 Current out of range %2.3f'%amps


    # set the current protection limit, after power_on this is 250mA
    def Amp_Protection(self,supply = 1, amps = 0.25):
        if supply != 1 and supply != 2 :
            print >> sys.stderr,'Error 2306 supply number either 1 or 2 %d'%supply
        else :
            if  amps <= 5.0 :
                if supply == 1 :
                    self.handle.write('SOUR1:CURR:LIM:VAL %2.3f'%amps)
                else :
                    self.handle.write('SOUR2:CURR:LIM:VAL %2.3f'%amps)
            else :
                print >> sys.stderr,'2306 Current out of range %2.3f'%amps



    # return actual current
    def Measure_Volts(self, supply = 1):
        if supply == 1 :
            return float(self.Query('MEAS1:VOLT?'))
        elif supply == 2 :
            return float(self.Query('MEAS2:VOLT?'))
        else :
            print >> sys.stderr,'Error 2306 supply number either 1 or 2 %d'%supply


    # return actual current
    def Measure_Amps(self,supply = 1):
        if supply == 1 :
            return float(self.Query('MEAS1:CURR?'))
        elif supply == 2 :
            return float(self.Query('MEAS2:CURR?'))
        else :
            print >> sys.stderr,'Error 2306 supply number either 1 or 2 %d'%supply


    def Display_On(self,disp = True):
        if disp == True :
            self.handle.write('DISP ON')
        else :
            self.handle.write('DISP OFF')

    def Display_Text(self,disp_text):
        if len(disp_text) > 10 :
            print >>sys.stderr,'Error 3640A display text string too long '
        else :
            self.handle.write('DISP:TEXT \' ' + disp_text + '\' ' )



# Testdrive the powersupply
#
def main():
    return False
# # check the instruments connected
#     gpib_instruments = visa.get_instruments_list()       # get instruments from VISA
#
#     print('Connected instruments : %s )'.format(gpib_instruments))
#
#     switch_2306 = False
#     print('Check if needed GPIB instruments are online')
#     for q in range(len(gpib_instruments)) :         # check all instruments in list
#         if gpib_instruments[q] == 'GPIB0::5' :
#             switch_2306 = True
#
#     if switch_2306 == True :
#         print('Online ==> Keithley 2306 at GPIB address 5'
#     else :
#         print '*** ERROR ***  Make sure 2306 is connected and turned ON (GPIB0::5)'
#
#     if switch_2306 == False  :
#         print 'Instrument problem, exit testprogram '
#         sys.exit(0)     # exit to OS
#
# # create object for the instruments
#     supply = Instrument_2306(0,5)
#
#     # check if GPIB error, exit if Yes
#     if supply.error == True :
#         print >>sys.stderr ,'Error Instrument not found, exit test'
#         sys.exit()
#
#
# # Testdrive the power-supply
# # set output to 0V, 1Amp max, output ON
#     # Supply 1
#     supply.Amp_Protection(1,0.25)
#     supply.Volt(1,10.0)
#     supply.Output_On(1,True)
#
#     # Supply 2
#     supply.Amp_Protection(2,0.25)
#     supply.Volt(2,11.5)
#     supply.Output_On(2,True)
#
#
#
# # set voltage protection limit
# #    supply.Volt_Protection(12.8)
#
#
# #    for a in range (10) :
#
#     # measure volts and current
#     volt1 = 0.0
#     amp1 = 0.0
#     volt2 = 0.0
#     amp2 = 0.0
#     for n in range(1):
#         for a in range (1,15+1,+1):
#             supply.Volt(1,a)
#             supply.Volt(2,a)
#             volt1 = supply.Measure_Volts(1)
#             amp1  = supply.Measure_Amps(1)
#             volt2 = supply.Measure_Volts(2)
#             amp2  = supply.Measure_Amps(2)
#             print '[1] %.3f V | %.4f A, %.3f Ohm '%(volt1,amp1,volt1/amp1) ,
#             print '[2] %.3f V | %.4f A, %.3f Ohm '%(volt2,amp2,volt2/amp2)
#             time.sleep(1)
#
#         for a in range (15,0,-1):
#             supply.Volt(1,a)
#             supply.Volt(2,a)
#             volt1 = supply.Measure_Volts(1)
#             amp1  = supply.Measure_Amps(1)
#             volt2 = supply.Measure_Volts(2)
#             amp2  = supply.Measure_Amps(2)
#             print '[1] %.3f V | %.4f A, %.3f Ohm '%(volt1,amp1,volt1/amp1) ,
#             print '[2] %.3f V | %.4f A, %.3f Ohm '%(volt2,amp2,volt2/amp2)
#             time.sleep(1)
#
#
#
#     supply.Output_On(1,False)
#     supply.Output_On(2,False)
#
#
#     print 'Done.....'



# boilerplate code for using either as Python module / main()
if __name__ == '__main__' :
    main()





