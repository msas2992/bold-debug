'''
Created on 1 jul. 2015

@author: e.schaeffer

updates 
17-07-2015 PdV    remove debug print statement (instrument list)
16-07-2015 ES   Init instrument list bug fix
'''



import visa
import time
import sys

# define Crestfactor, can be either 3 or 6, default 3
CRESTFACTOR = 3



# the Yokogawa WT310 power meter, controlled via USB

class Instrument_WT310_USB():
    errorstr = ''

    def __init__(self, vid, pid):
        # connect the WT310 instrument via USB
        self.WT310_error = False
        self.errorstr = ''
        # get connected instrument list
        try:
            rm = visa.ResourceManager()
            instruments = rm.list_resources()

        except:
            self.WT310_error = True
            return

        # check if USB instrument with proper PID / VID in instrument list

        # start with error True
        self.WT310_error = True
        # check the list
        for instr in instruments:
            if ('USB' in instr) and (str(vid) in instr) and (str(pid) in instr):
                try:
                    self.handle = rm.open_resource(instr)
#                     self.handle = visa.Instrument(instr)
                    self.WT310_error = False
                    break
                except:
                    print >> sys.stderr, 'Error connecting WT310'
                    self.WT310_error = True
                    return

        if self.WT310_error == True:
            self.errorstr = 'Instrument WT310 not found'
            return

        idn_string = self.Query('*IDN?')
        if 'WT310' in idn_string :
            #print 'WT310 recognised'
            pass
        else :
            self.errorstr = 'WT310 Wrong IDN response : %s'%idn_string
            print >> sys.stderr, self.errorstr
            self.WT310_error = True
            return

        self.Initialize()


    # send command to instrument
    # read response
    def Query(self,command = '*IDN?'):
        self.handle.write(command)
        time.sleep(0.1)     # recovery time
        return self.handle.read()


    # perform *STB?, when bit EAV == 1 => check error type
    def Check_Error(self):
        self.stb_result = int(self.Query('*STB?'))
        if (self.stb_result & 0x04) != 0 :
            sys.stderr.write('WT310 Error %s'%self.Query('STATUS:ERROR?'))


    # reset all channels to 'OPEN'
    def Reset(self):
        print(self.Query('*IDN?'))

#        self.handle.write('*RST')
#        self.handle.write('*CLS')   # reset errors


    def Initialize(self):
        # settings to instrument
        self.handle.write('*RST')                   # reset instrument
        self.handle.write('*CLS')                   # clear previous errors

        # new commands
        self.handle.write('COMM:REMOTE 1')          # place instrument in remote mode
        self.handle.write('COMM:HEADER 0')          # disable response headers
        self.Check_Error()

        # configure the instrument displays
        # display A (U I P S Q TIME)
        self.handle.write('DISP:NORM:ITEM1 U')     # display A = Mains voltage
        # display B (U I P LAMBDA PHI)
        self.handle.write('DISP:NORM:ITEM2 I')     # display B = Current
        # display C (U I P UPPeak UMPeak IPPeak IMPeak PPPeak PMPeak WHP WHM AH AHP AHM MATH)
        self.handle.write('DISP:NORM:ITEM3 P')     # display C = Power
        # display D (U I P LAMBDA FU FI UTHD ITHD)
        self.handle.write('DISP:NORM:ITEM4 U')    # display D = Mains frequency
        self.Check_Error()

        # instrument wiring => P1W2 (single phase 2 wire)
        self.handle.write('INPUT:WIRING P1W2')

        # instrument Crest factor either 3 or 6 (check Volt range !!)
        self.handle.write('INPUT:CFACTOR 3')
        # input mode DC /RMS / VMean
        self.handle.write('INPUT:MODE RMS')             # mode RMS

        # input Voltage range, depends on Crest factor
        # Crest = 3 => 15 30 60 150 300 600V
        # Crest = 6 => 7.5 15 30 75 150 300V
        self.handle.write('INPUT:VOLTAGE:RANGE 300')    # 300V

        # Input Current range, depends on Crest factor
        # Crest = 3 => 5 10 20 50 100 200 500 mA 1 2 5 10 20 A
        # Crest = 6 => 2.5 5 10 25 50 100 250 500 mA 1 2.5 5 10 A
        self.crest = CRESTFACTOR
        self.handle.write('INPUT:CURRENT:RANGE 100mA')       # 100mA

        # instrument sync source
        self.handle.write('INPUT:SYNC Voltage')
        self.Check_Error()

        # filter settings
        self.handle.write('INPUT:FILTER:LINE 0')
        self.handle.write('INPUT:FILTER:FREQ 0')

        # averaging
        # Linear / Exponent
        self.handle.write('MEAS:AVERAGING:TYPE LINEAR')
        # average count 8 16 32 64
        self.handle.write('MEAS:AVERAGING:COUNT 8')
        # max hold on/off state => off
        self.handle.write('MEAS:MHOLD 0')

        # Numeric group
        # set the numeric format ASCII / FLOAT
        self.handle.write('NUMERIC:FORMAT ASCII')

        # experiment
        self.handle.write('STATUS:FILTER1 FALL')

        # dummy read EESR register
        dummy = self.Query('STATUS:EESR?')


    # set current range in A steps
    # Crest = 3 => 0.005 0.010 0.020 0.050 0.100 0.200 1 2 5 10 20 A
    # Crest = 6 => 0.0025 0.005 0.010 0.025 0.050 0.100 0.250 0.500 1 2.5 5 10 A
    def Set_Range_Amp(self, amp = '20A'):
        self.handle.write('INPUT:CURRENT:RANGE %s'%amp)
        self.Check_Error()
        return self.Query('INPUT:CURRENT:RANGE?')


    # set Voltage range in V steps
    # depends on selected Crest factor
    def Set_Range_Volt(self, volt = '600V'):
        self.handle.write('INPUT:VOLTAGE:RANGE %s'%volt)
        self.Check_Error()
        return self.Query('INPUT:VOLTAGE:RANGE?')


    # prepare the instrument to take a fresh sample, return all results as string
    def Sample_New_Data(self):
        # comm wait will wait for bit 0 in Exteneded Event Register to be 1
        self.handle.write('COMM:WAIT 1')
        result_string = self.Query('Num:NORM:Val?')
        dummy = self.Query('STATUS:EESR?')
        return result_string


    # wait for measurement done and get results,
    # return tuple with V,A,W,Hz
    def Get_VAWF(self):
        result_list = self.Sample_New_Data().split(',')
        Volt = float(result_list[0])
        Amp  = float(result_list[1])
        Watt = float(result_list[2])
        Freq = float(result_list[7])
        self.Check_Error()
#        print 'Volt %.2f V Amp %.2f A Power %.2f W Freq %.2f Hz'%(Volt,Amp,Watt,Freq)
        return(Volt,Amp,Watt,Freq)

    def setDisplay(self, num, func):
        self.handle.write('DISP:NORM:ITEM{:d} {:s}'.format(num, func))
        



if __name__ == '__main__':
    rm = visa.ResourceManager()
    print(rm.list_resources())
    
    
# 
#  # testdrive the powermeter
# if __name__ == '__main__' :
#     print('Start WT310 sample')
#     pwr = Instrument_WT310_USB('0x0B21','0x0025')
#     if pwr.WT310_error == True :
#         print('Error USB connection WT310')
#         sys.exit()
# 
# 
#     pwr.Initialize()
#     print 'Current range :' + pwr.Set_Range_Amp('50mA')
# 
# 
#     print 'Current range :' + pwr.Set_Range_Volt('300V')
#     for n in range(5) :
#         print 'Volt %f Amp %f Pwr %f Freq %f'%(pwr.Get_VAWF())
# 
#     print 'Done'
