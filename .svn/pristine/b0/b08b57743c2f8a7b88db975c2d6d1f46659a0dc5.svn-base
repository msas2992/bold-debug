#!/usr/local/bin/python
#
# low level commands for Agilent E6632A
#
# powersupply 0-15V/7A or 0-30V/4A
# PdV 16-10-2014 add *IDN? to check for proper instrumment
# PdV 07-02-2013

import visa
import time
import sys


class Instrument_E3632A:
    # constructor, open and init gpib channel, init instrument
    def __init__(self, board = 0, addr = 12):
        try :
            self.handle = visa.GpibInstrument('GPIB%s::%s'%(board,addr))
            # instrument in FactoryReset state , reset status bits
            self.handle.write('*RST ; *CLS')
        except :    # all errors
            print >> sys.stderr, 'Error instrument E3632A GPIB address'
            self.error = True
            return
        
#        # check if this is a real E3632A
        idn_response = self.Query('*IDN?')
        if not 'E3632A' in idn_response :
            print >> sys.stderr, 'Error instrument E3632A *IDN?'            
            self.error = True            
            return
      
        self.handle.write('SOUR:VOLT:PROT:STATE OFF')
        self.handle.write('SOUR:CURR:PROT:STATE OFF')
        self.handle.write('*RST; *CLS')
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

  
    def Output_On(self):
            self.handle.write('OUTP:STATE ON')
        
    def Output_Off(self):
            self.handle.write('OUTP:STATE OFF')
            
    def Set_High_Range(self,rng=True):
        if rng == True :
            self.handle.write('SOUR:VOLT:RANG P30V')
            self.high_range = True
        else :
            self.handle.write('SOUR:VOLT:RANG P15V')
            self.high_range = False
            

    # set the output voltage
    def Volt(self,volts = 0.0):
        if (volts <= 15.0) :
            self.handle.write('SOUR:VOLT:LEV %2.3f'%volts)
        elif volts <= 30 :
            if self.high_range == False :
                self.Set_High_Range(True)
            self.handle.write('SOUR:VOLT:LEV %2.3f'%volts)
        else :
            print >> sys.stderr,'E3632A Voltage out of range %2.3f'%volts    
        
    # set the max output current
    def Amp(self,amps = 0):
        if ((self.high_range == True and amps <= 4) or \
                (self.high_range == False and amps <= 7)) :
            self.handle.write('SOUR:CURR:LEV %2.3f'%amps)
        else :
            print >> sys.stderr,'E3632A Current out of range %2.3f'%amps    
 
    # set protection voltage
    def Volt_Protection(self,volts = 5.0):
        if volts <= 30 :
            self.handle.write('SOUR:VOLT:PROT:LEV %2.3f'%volts)
            self.handle.write('SOUR:VOLT:PROT:STATE ON')
        else :
            print >> sys.stderr,'E3632A protection Voltage out of range %2.3f'%volts    
            
    # return True when OverVoltaged        
    def Volt_Tripped(self):
        if self.Query('SOUR:VOLT:TRIP?') == '1' :
            return True
        else :
            return False
 
    # reset overvoltage trip
    def Volt_Trip_Reset(self):
            self.handle.write('SOUR:VOLT:PROT:CLEAR')
   
    # return actual current 
    def Measure_Volts(self):
        return float(self.Query('MEAS:VOLT?'))
   

    # set protection current
    def Amp_Protection(self,amps=1.0):
        if ((self.high_range == True and amps <= 4.0) or \
                (self.high_range == False and amps <= 7.0)) :
            self.handle.write('SOUR:CURR:PROT:LEV %2.3f'%amps)
            self.handle.write('SOUR:CURR:PROT:STATE ON')
            
        else :
            print >> sys.stderr,'E3632A Protection Current out of range %2.3f'%amps    

    # return True when OverCurrentTripped        
    def Amp_Tripped(self):
        if self.Query('SOUR:AMP:TRIP?') == '1' :
            return True
        else :
            return False
        
    # reset overcurrent trip
    def Amp_Trip_Reset(self):
        self.handle.write('SOUR:AMP:PROT:CLEAR')
       
    # return actual current 
    def Measure_Amps(self):
        return float(self.Query('MEAS:CURR?'))
               
  
  
# Testdrive the powersupply
#
def main():
    
# check the instruments connected    
    gpib_instruments = visa.get_instruments_list()       # get instruments from VISA

    print 'Connected instruments : %s '%gpib_instruments
    
    switch_E3632A = False
    print 'Check if needed GPIB instruments are online'
    for q in range(len(gpib_instruments)) :         # check all instruments in list
        if gpib_instruments[q] == 'GPIB0::23' :
            switch_E3632A = True

    if switch_E3632A == True :
        print 'Online ==> E3632A at GPIB address 23'
    else :
        print '*** ERROR ***  Make sure E3633A is connected and turned ON (GPIB0::23)'
        
    if switch_E3632A == False  :
        print 'Instrument problem, exit testprogram '
        sys.exit(0)     # exit to OS

# create object for the instruments
    supply = Instrument_E3632A(0,23)
    
    # check if GPIB error, exit if Yes
    if supply.error == True :
        print >>sys.stderr ,'Error Instrument not found, exit test'
        sys.exit()
        
    
    
# set output to 0V, 1Amp max, output ON
    supply.Set_High_Range(True)
    supply.Amp(1.2)
    supply.Volt(12.0)
    supply.Output_On()

# set voltage protection limit    
    supply.Volt_Protection(12.8)
    
# set amp protection level
    supply.Amp_Protection(1.5)
    
    # measure volts and current
    for n in range (10):
        print 'Voltage = %2.2f V Current = %2.4f A '%(supply.Measure_Volts(), supply.Measure_Amps()) 
        time.sleep(.5)

    supply.Volt(0.0)
    
    print 'Done.....'

    
    
# boilerplate code for using either as Python module / main()   
if __name__ == '__main__' :
    main()





