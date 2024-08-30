'''
Created on 1 jul. 2015

@author: e.schaeffer
'''

'''

Testdrive the relay I/O board


'''



from Instruments.SerialInterface import SerialInterface
import time
import sys

class USBRelay():
    def __init__(self, comport) :
        self.error = False
        try :
            self.ser = SerialInterface(comport,
                              timeout=0.05,
                              baudrate=115200
                              )
        except Exception as e:
            print(e)
            print('USB connection / Comport nr ERROR')
            self.error = True
            return

        # connection is made
        # send some dummy newlines to make sure the banner is passed
        for n in range (1) :
            self.ser.write('\n')
            time.sleep(.2)

        # switch OFF the halfduplex echo
        self.ser.write('echo 0\n')
        time.sleep(.2)
        # read multiple lines, the board is sending CR/LF if there is no tomorrow
        ser_buf = self.ser._readlines()
        if 'echo 0'  not in ser_buf :
            print('Board problem, echo command')
            self.error = True
            return

        # make sure IO mode is enabled (mode = 1)
        # first ask for mode, when 1 => OK
        # else perform mode 1 command
        self.ser.flushInput()
        self.ser.write('mode \n')
        time.sleep(.1)
        try :
            self.mode = int(self.ser._readline())
            if self.mode != 1 :
                self.ser.write('mode 1 \n')
                time.sleep(.1)
        except :
            self.error = True
            return

    def Clear_BootMessage(self):
        # dummy write to clear welcome message
        self.ser.write('\n')

    def Set_Relay(self,nr=0):
        if nr in [0,1] :
            self.ser.write('set %d \n'%nr)
        else :
            print('Error relay number')

    def Clr_Relay(self,nr=0):
        if nr == 0 or nr == 1 :
            self.ser.write('clr %d \n'%nr)
        else :
            print('Error relay number')

    def Get_Input(self,nr=0):
        if nr in [4,3,2,1,0] :
            self.ser.flushInput()
            self.ser.write('in %d\n'%nr)
            time.sleep(.1)
            ser_buf = self.ser._readline()
            try :
                result = int(ser_buf)
            except :
                return None
            return result

    # close serial port
    def Close_UsbRelay_Channel(self):
        self.ser.close()


 
# Standalone run, without GUI !!
if __name__ == '__main__':
 
    print('Testdrive the Relay IO board ')
    
    test = USBRelay('COM5')
    
    print('asdasdasd')
    
    if test.error == True :
        print('Serial port error')
        sys.exit()
 
    num  = 0
 
    for n in range(10):
        test.Clr_Relay(0)
        time.sleep(0.5)

        inputs = []
        for i in [0,1,2,3,4]:
            inputs.append(test.Get_Input(i))       
        print('Input levels:', inputs) 

        test.Set_Relay(0)
        time.sleep(0.5)

        inputs = []
        for i in [0,1,2,3,4]:
            inputs.append(test.Get_Input(i))       
        print('Input levels:', inputs) 

    test.Close_UsbRelay_Channel()


#     for n in range (200) :
# #        test.Set_Relay(0)
#         inport = test.Get_Input(2)
#         if inport != None :
#             print  inport
#
#             if inport == 1 :
#                 if num >20:
#                     test.Clr_Relay(1)
#                 else:
#                     test.Set_Relay(1)
#                 num += 1
#
#             else :
#                 num = 0
#                 test.Clr_Relay(1)
#
#
#         else :
#             print 'Big Problem Get data'
