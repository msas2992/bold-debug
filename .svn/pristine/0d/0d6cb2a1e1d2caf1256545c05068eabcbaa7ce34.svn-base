#!/usr/local/bin/python
#
# low level commands for Admesy Hyperion
#    Colorimeter
#
# 
# PdV 29-07-2015
# Updates


import visa
import time
import sys
from pprint import pprint       # extended print ==> pprint() (pretty output)
import struct


# retrieve SCPI commands from instrument driver
class SCPI():
    # send command to instrument
    # read response
    def Query(self, command = '*IDN?'):
        try :
            self.handle.write(command)
            time.sleep(0.1)     # recovery time
        except :
            sys.stderr.write('Error instrument Query command %s'%command)
            return None

        return self.handle.read()
    
    def Command(self, command):
        try :
            self.handle.write(command)
        except :
            sys.stderr.write('Error instrument Query command %s'%command)
            return None

       
    # reset all channels to 'OPEN'  
    def Reset(self):
        try :
            self.handle.write('*RST')        
            self.handle.write('*CLS')   # reset errors
        except :  
            sys.stderr.write('Error instrument Reset command')
            return None


# inherit above SCPI commands
class Instrument_Hera(SCPI):

    def __init__(self):
        self.handle = None
    
    # check instruments connected to VISA return the USB vd,pid instrument
    # return the instrument name
    def find_usb_instrument(self, vid, pid):
        try:
            rm = visa.ResourceManager()
            instruments = rm.list_resources()
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
                #self.handle = visa.Instrument(instr)                
                rm = visa.ResourceManager()
                self.handle = rm.open_resource(instr)
            except:
                print >> sys.stderr, 'Error connecting camera'
                return False
        else:
            print >> sys.stderr, 'ERROR, no colorimeter found'
            return False
        return True
 
            
    # ========================================================
    # instrument commands
    
    # Get result from Brontes, perform the amount of samples
    # defined with the :SENSE:AVERAGE command and return the
    # average of these measurements   
    def measure_Yxy(self):
        result = self.Query(':MEAS:Yxy')

        result = result.split(',')

        Yxy = {}
        Yxy['Y'] = float(result[0])
        Yxy['x'] = float(result[1])
        Yxy['y'] = float(result[2])

        #return self.Query(':MEAS:Yxy')
        
        return Yxy


    # take several samples and store in camera, finally read data in one action
    # from camera
    # take care for buffer overflow in camara
    # return RAW data
    def sample_Yxy(self, numsamples=1000):
        # get binary string from camera
        # command = SAMPLE:Yxy Samples Delay
        # Samples = number of samples wanted, max 4000
        # Delay = 0
        ret = self.Query(':SAMP:Yxy {:d},0'.format(numsamples))  

#        print 'Len Admesy return string %d'%len(ret)
        # for some reason the string from camera is missing 1 byte
        # this will result in fatal error for struct.unpack, just try again
#        print 'Len = %d'%len(ret)
        try :
            # convert binary string to float array
            # > little / big endian
            # {:d} = number of samples presented
            # f = retrieve and convert floats from bin string (ret)
            # result = 3 floats per sample 
            # +3 is CLIP / NOISE / dt
            # all floats are 4 bytes
            # len string 1000 samples = (1000 * 3 + 3) * 4 (4 length float)
            a = struct.unpack('>{:d}f'.format(numsamples*3 + 3), ret)
        except :
            ret = self.Query(':SAMP:Yxy {:d},0'.format(numsamples))  
            a = struct.unpack('>{:d}f'.format(numsamples*3 + 3), ret)
            
        buf = ''
        # camera specific data in first 3 floats
        buf += 'dt    {:.3f}\n'.format(a[0])
        buf += 'clip  {:.3f}\n'.format(a[1])
        buf += 'noise {:.3f}\n'.format(a[2])
        buf += '\n\n'
        
#        print buf
        
        # print buffer nice on screen
        for i in range(numsamples):
            buf += '{:4d}: {:.3f}  {:.3f}  {:.3f}\n'.format(i, 
                                                         a[3+i*3], 
                                                         a[4+i*3], 
                                                         a[5+i*3]) # (index i)
#        print buf
#        return buf
        return a
    
    # set number of samples the Brontes will take per measurement
    # Important to have the samples fit as close as possible in the PWM periode
    def set_average(self, samples):
        self.Command(':SENS:AVER {:d}'.format(samples))
    
    
    # return Flicker
    def get_flicker(self, samples=2000):
        result = self.Query(':MEAS:FLIC {:d}'.format(samples))

        return float(result)


    # set Brontes Gain
    # 0 .... 8 
    # 0 = auto
    # 1 is highest gain
    def set_gain(self, gain = 0):
        if gain >= 0 and gain <= 8 :
            self.Command(':SENS:GAIN {:d}'.format(gain))
        

    # FInd optimum gain 
    def Find_Optimal_Gain(self):
        for gain in range(1,9) :
            self.set_gain(gain)
            buf = self.sample_Yxy(1000)
            if buf[1] == 0 :
#                print 'gain = %d'%gain
#                print 'Set gain %d'%(gain)
                self.set_gain(gain)
                break




    
    # set caibration matrix
    # small wide off user1 user2 user3
    def Set_Cal_Matrix(self,matrix = "small") :    
        if matrix in 'small wide off user1 user2 user2' :
            self.Command(':SENSE:SBW {:s}'.format(matrix))
        else :
            print >> sys.stderr,'Set_Cal_Matrix invalid matrix {:s}'.format(matrix)
        









# Testdrive Instrument    
# boilerplate code for using either as Python module / main()   
if __name__ == '__main__' :
    HP = Instrument_Hera()
     
    #
#    BR.connect_usb('0x1781','0x0E93')
    HP.connect_usb('0x23CF','0x1021')
    HP.Reset()
    ret = HP.Query(':MEAS:Yxy')
    print(ret)
# 
#     # define average samples / measurement
# #    BR.Command(':SENS:AVER 277')
# #    HP.Command(':SENS:AVER 4')
#     
#     
#     
# #    HP.set_gain(0)
# #    print 'Hyperion Gain = %s'%HP.Query(':SENS:GAIN?')      # OK
#     
#     # get nr average setting from camera
# #    ret = HP.Query(':SENS:AVER?')
# #    print('average = %s'%ret)                               # OK
# 
# 
#     # return cal matrix
# #    print HP.Query(':SENS:SBW?')
# 
#     # Flicker?
# #    print 'Flicker %s'%HP.Query(':MEAS:FLICKER')            # write FLICKER FULL, NO number behind
#     
# # Set Autogain 1 = on 0 = off
#     HP.Command(':SENS:AUTORANGE 1')
# # not sure if we can use sense:gain? when automode = 1
# 
# # set Manual gain 1 2 3
# #    HP.Command(':SENS:GAIN 1')
# #    print 'Hyperion Gain = %s'%HP.Query(':SENS:GAIN?')      # OK
# 
# # For autorange it seems to be important to define the sample window upfront, make sure
#     
#     # Measure Yxy
#     for n in range (100) :
#         print 'Yxy %s'%HP.Query(':MEAS:Yxy') 
#     
#     start = time.time()
#     '''
#     for n in range(10) :
#         print HP.measure_Yxy()  
#     
#     print 'Admesy Gain = %s'%HP.Query(':SENS:GAIN?')
#     '''
#     '''
#     for n in range(10) :
#         buf = BR.sample_Yxy(2)
#     
#     # write formatted buffer to file
#     with open('test4.txt', 'w') as fd:
#         fd.write(buf)
#     '''
#     end = time.time()
#     
#     print 'Run time {:.3f} Sec \n'.format(end-start)
# 



