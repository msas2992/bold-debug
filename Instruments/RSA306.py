'''
Created on 25 apr. 2017

@author: e.schaeffer
'''
import sys
import time

import vxi11


frequencies = {
    1: 2.412E9,
    2: 2.417E9,
    3: 2.422E9,
    4: 2.427E9,
    5: 2.432E9,
    6: 2.437E9,
    7: 2.442E9,
    8: 2.447E9,
    9: 2.452E9,
    10: 2.457E9,
    11: 2.462E9,
    12: 2.467E9,
    13: 2.472E9,
    14: 2.477E9           
}


class Instrument_RSA306():  
    # constructor, open and init VXI-11 channel, init instrument
    def __init__(self):
        try :
            self.instr = vxi11.Instrument("localhost")

            # instrument in FactoryReset state , reset status bits
            self.instr.write("*CLS")

            self.error = False
        except  :
            print('Error instrument RSA306B VXI-11')
            self.error = True

    # send command and check for error
    def SendCommand(self,command = None):
        if command != None :
            self.instr.write(command)
            result = self.instr.ask("*STB?")
            if int(result) != 0 :
                print(command + " ERROR " + result)
                print("*ESR? = " + self.instr.ask("*ESR?"))
                self.instr.write("*CLS")
    

    # init the analyser
    def Init_Analyser(self):      
        # reset instrument
        self.instr.write("*CLS")
#       print("*STB? = " + self.instr.ask("*STB?"))
#       print("*ESR? = " + self.instr.ask("*ESR?"))
 
        # select internal or extern reference

    def getFrequencyChannel(self, channel):
        if channel not in frequencies:
            return (None, None)
        
        freq = frequencies[channel]
        
        return self.getFrequency(int(freq))

    def getFrequency(self, freq):
        print('measuring frequency', freq)
        # instrument preset, start in a defined state
        # this will remove the cursors !
        self.SendCommand("system:preset")
        
        # Set number of sample points in spectrum
        self.SendCommand("SENSe:SPECtrum:POINts:COUNt P8001")
        
       
        # adjust center frequency and span 10MHz
        self.SendCommand("SENSe:spectrum:FREQuency:CENTer {:s}".format(str(freq)))
        self.SendCommand("SENSe:spectrum:FREQuency:span 10MHz")
 
        # MARKER 
        # add marker : MR (reference) 
        self.SendCommand("CALCULATE:MARKER:ADD")
 
        # select a decent reference level
        self.SendCommand("input:rlevel -20dBm")


        # enable trace1 and trace2, trace2 just for checking the mechanism on the screen
        self.SendCommand("TRACE1:SPECTRUM ON" )      # enable the YELLOW trace
        self.SendCommand("TRACE2:SPECTRUM ON" )      # enable the BLUE trace maxhold

        # function of the trace None Average maxhold etc
        self.SendCommand("TRACe1:SPECtrum:FUNCtion NONE") 
        self.SendCommand("TRACe1:SPECtrum:DETection AVERAGE" )

        # add another trace with MAXHOLD
        self.SendCommand("TRACe2:SPECtrum:FUNCtion MAXHOLD") 
        self.SendCommand("TRACe2:SPECtrum:DETection AVERAGE" )


        # make sure we have a signal to lock the marker
        # let the analyser sample the spectrum span
        time.sleep(.5)

        # find max signal in displayed spectrum @ M1
        self.SendCommand("CALCULATE:SPECTRUM:MARKER0:Maximum")
        
        # set the center frequency to M1
        self.SendCommand("CALCulate:SPECtrum:MARKer0:SET:CENTer")

        # auto scale the waveform in the Y scale
        self.SendCommand("DISPlay:SPECtrum:Y:SCALE:AUTO" )
        
        # scale per division in Y (e.g. 10dBm/div) 2-5-10 etc
        # default = 10dBm
        self.SendCommand("DISPlay:SPECtrum:Y:SCALe:PDIVision 10" )
 
 
        #
        # step 2
 
        # reduce the span and the RBW to gain accuracy
        self.SendCommand("SENSe:spectrum:FREQuency:span 100kHz")
        
        # set RBW 100Hz
        self.SendCommand("SENSE:SPECTRUM:BANDWIDTH:RESOLUTION 1kHz")

        # make sure we have a signal to lock the marker
        # let the analyser sample the spectrum span
        time.sleep(1.0)
 
        # find max signal in displayed spectrum @ M1
        self.SendCommand("CALCULATE:SPECTRUM:MARKER0:Maximum")
        
        # set the center frequency to M1
        self.SendCommand("CALCulate:SPECtrum:MARKer0:SET:CENTer")

        # auto scale the waveform in the Y scale
        self.SendCommand("DISPlay:SPECtrum:Y:SCALE:AUTO" )

        # make sure we have a signal to lock the marker
        # let the analyser sample the spectrum span
        time.sleep(1.0)

        '''
        #
        # step 3
 
        # reduce the span and the RBW to gain accuracy
        self.SendCommand("SENSe:spectrum:FREQuency:span 10kHz")
        
        # set RBW 100Hz
        self.SendCommand("SENSE:SPECTRUM:BANDWIDTH:RESOLUTION 100Hz")

        # make sure we have a signal to lock the marker
        # let the analyser sample the spectrum span
        time.sleep(1.0)
 
         # find max signal in displayed spectrum @ M1
        self.SendCommand("CALCULATE:SPECTRUM:MARKER0:Maximum")
        
        # set the center frequency to M1
        self.SendCommand("CALCulate:SPECtrum:MARKer0:SET:CENTer")

        # auto scale the waveform in the Y scale
        self.SendCommand("DISPlay:SPECtrum:Y:SCALE:AUTO" )

        # make sure we have a signal to lock the marker
        # let the analyser sample the spectrum span
        time.sleep(1.0)
        '''

        measfreq  = float(self.instr.ask("CALCulate:SPECtrum:MARKer0:X?"))
        measlevel = float(self.instr.ask("CALCulate:SPECtrum:MARKer0:Y?"))

        return (measfreq, measlevel)


if __name__ == '__main__':
    rsa = Instrument_RSA306()
    
    rsa.Init_Analyser()
#     ret = rsa.getFrequency(2432000000)
    ret = rsa.getFrequencyChannel(5)
    print(ret)
    
    
    