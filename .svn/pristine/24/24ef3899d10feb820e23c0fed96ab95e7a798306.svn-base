'''

Testdrive the LSCT AntennaBox

P de Vroome
    Updates :
    20-07-2015  PdV test for Admesy colormeter
                    implement toolreset, 
    15-07-2015  PdV
                Implement RSSI filter and SetTxPower 
    08-05-2015



'''
from pprint import pprint
import random
import sys
import time

from Instruments.SerialInterface import SerialInterface


# import usbrelay
class FactoryLinkTool(SerialInterface):
    verbose = False
    MAC = None
    factory_new = False
    BuildId = None
    channel = None

    # serial port parameters are passed while creating the object
    def __init__(self, *args, **kwargs):
        SerialInterface.__init__(self, *args, **kwargs)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Method 'Niels'
    # After PowerOn / Reset :
    # due to ram limitations we have to send just '[]\r'
    # until response '[SYS,Error,Incorrect format]\r'
    # wait 100mS between command and check for response
    # repeat max 20 times
    # perform colortest init
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def BoardAllocateSerialBuffer(self):
        for n in range (20) :            
            self.flushInput()
            self.write('[]\r')
            
            # wait for proper response, max 200mS
            ser_buf = self._readline(timeout = 0.2)   # wait for response
            if '[SYS,Error,Incorrect format]\r' in ser_buf :
                return True
        return False


    # channel mask see above
    def ToolReset(self):
        self.flushInput()
        self.write('[FT,ToolReset]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readlines(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if '[FT,Ready]' not in ser_buf :
            return False
        
        lines = ser_buf.split('\n')
        for line in lines:
            if 'Product version FactoryLinkTool' not in line:
                continue
            data = line.split(',')
            for dd in data:
                if not dd.startswith('Product version FactoryLinkTool'):
                    continue
                d = dd.split(' ')
                version = d[3]
                print('Product version FactoryLinkTool', version)    
        
        return True


    # channel_mask = channel
    # 0x00000800    = 11
    # 0x00001000    = 12
    # 0x00002000    = 13
    # 0x00004000    = 14
    # 0x00008000    = 15
    # 0x00010000    = 16
    # 0x00020000    = 17
    # 0x00040000    = 18
    # 0x00080000    = 19
    # 0x00100000    = 20
    # 0x00200000    = 21
    # 0x00400000    = 22
    # 0x00800000    = 23
    # 0x01000000    = 24
    # 0x02000000    = 25
    # 0x04000000    = 26
    # 0x07FFF800    = 11 .... 26
    # 0x02108800    = 11,15,20,25
    def SetChannelMask(self,channel_mask = '0x02108800'):
        self.flushInput()
        self.write('[FT,SetChannelMask,%s]\r'%channel_mask)

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if '[FT,SetChannelMask,0]\r' in ser_buf:
            return True
        return False


    # channel mask see above
    def BindLight(self, channel_mask = '0x02108800'):
        self.flushInput()
        self.write('[FT,BindLight,%s]\r'%channel_mask)

        # wait for command accepted, max 200mS
        ser_buf = self._readline(timeout = 3.2)   # wait for response
        if self.verbose:
            print(ser_buf)
            
        if not '[FT,BindLight,0]\r' in ser_buf:
            return False

        self.flushInput()
        # wait for actual binding, max 8 S
        ser_buf = self._readline(timeout =10.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,BindLightRsp,0]\r' in ser_buf:
            return False

        return True


    # check factory new
    def CheckLightFN(self):
        self.factory_new = False
        self.flushInput()
        self.write('[FT,CheckLightFN]\r')

        # wait for command accepted, max 200mS
        ser_buf = self._readline(timeout = 4.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,CheckLightFN,0]\r' in ser_buf :
            return False

        self.flushInput()
        # wait for response, max 8 S
        ser_buf = self._readline(timeout = 10.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,CheckLightFNRsp,0' in ser_buf :
            return False

        try:
            ser_buf = ser_buf.strip().strip('[]').split(',')
            if int(str(ser_buf[3])) == 0:
                self.factory_new = True
            elif int(str(ser_buf[3])) == 4:
                self.factory_new = False
            else:
                self.factory_new = None
                return False
        except:
            return False

        return True


    def GetBuildId(self):
        self.BuildId = None

        self.flushInput()
        self.write('[FT,GetBuildId]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,GetBuildId,0' in ser_buf :
            return None

        ser_buf = ser_buf.strip().strip('[]').split(',')
        self.BuildId = ser_buf[3]

        return ser_buf


    def GetDeviceId(self):
        self.DeviceId = None

        self.flushInput()
        self.write('[FT,GetDeviceId]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,GetDeviceId,0' in ser_buf :
            return None

        ser_buf = ser_buf.strip().strip('[]').split(',')
        self.DeviceId = ser_buf[3]

        return ser_buf


    def GetMac(self):
        self.MAC = None
        self.flushInput()
        self.write('[FT,GetMac]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
            
        if not '[FT,GetMac,0' in ser_buf :
            return False

        ser_buf = ser_buf.strip().strip('[]').split(',')
        self.MAC = ser_buf[3]

        return True


    def GetChannel(self):
        self.channel = None
        self.flushInput()
        self.write('[FT,GetChannel]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,GetChannel,0' in ser_buf :
            return False

        ser_buf = ser_buf.strip().strip('[]').split(',')
        self.channel = ser_buf[3]

        return True

    def GetLampNumber(self):
        self.channel = None

        ret = self._readattr(0x1000, 0x100b, 0xf100)

        try:
            self.lampnumber = '{:06X}'.format(int(ret[4]))
        except:
            self.lampnumber = '------'
            return False

        return True


    def GetFirmwareVersion(self):
        ret = self._readattr(0x0000, 0x0000, 0x4000)
        if ret is False:
            return False

        try:
            self.firmwareversion = '{:s}'.format(ret[4])
        except:
            self.firmwareversion = '------'
            return False

        return True


    def GetHardwareVersion(self):
        ret = self._readattr(0x0000, 0x0000, 0x0003)
        if ret is False:
            return False

        try:
            self.hardwareversion = '{:s}'.format(ret[4])
        except:
            self.hardwareversion = '------'
            return False

        return True


    def GetModelId(self):
        ret = self._readattr(0x0000, 0x0000, 0x0005)
        if ret is False:
            return False

        try:
            self.modelID = '{:s}'.format(ret[4])
        except:
            self.modelID = '------'
            return False

        return True


    def _readattr(self, clusterid, manufcode, attributeid):
        self.flushInput()
        self.write('[FT,ReadAttr,0x{:04x},0x{:04x},0x{:04x}]\r'.format(clusterid,
                                                                       manufcode,
                                                                       attributeid))

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,ReadAttr,0' in ser_buf :
            return False

        ser_buf = self._readline(timeout = 2.2)   # wait for response
        if self.verbose:
            print(ser_buf)
            
        if not '[FT,ReadAttrRsp,0' in ser_buf :
            return False

        ser_buf = ser_buf.strip().strip('[]').split(',')
        return ser_buf


    def GetKeyBitMask(self):
        self.flushInput()
        self.write('[FT,GetKeyBitMask]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,GetKeyBitMask,0' in ser_buf :
            return False
        return ser_buf


    def LightReset(self):
        self.flushInput()
        self.write('[FT,LightResetFN]\r')

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,LightResetFN,0' in ser_buf :
            return False

        # wait for response, max 8 S
        ser_buf = self._readline(timeout = 10.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not 'FT,LightResetFNRsp,0]\r' in ser_buf :
            return False

        return True


    def SetHueSat(self,hue = 25600, sat = 250, transition = 0):
        self.flushInput()
#        self.ser.write('[FT,MoveToEnhancedHueAndSat,25600,200,0]\r')
#        print '[FT,MoveToEnhancedHueAndSat,25600,200,0]\r'
        self.write('[FT,MoveToEnhancedHueAndSat,%d,%d,%d]\r'%(hue,sat,transition))

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,MoveToEnhancedHueAndSat,0' in ser_buf :
            return None
        return ser_buf

        self.flushInput()
        # wait for response, max 8 S
        ser_buf = self._readline(timeout = 10.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not 'FT,MoveToEnhancedHueAndSatRsp,0]\r' in ser_buf :
            return False

        return True
    
    
    def setColortempMired(self, colortemp=250, transition=0):
        CMD = 'MoveToColorTemperature'
        self.flushInput()
        
        ct = int(1000000 / colortemp)
        #ct = colortemp 
        
        self.write('[FT,{:s},{:d},{:d}]\r'.format(CMD,
                                                  ct,
                                                  transition))

        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,{:s},0'.format(CMD) in ser_buf :
            return None
        return ser_buf

        self.flushInput()
        # wait for response, max 8 S
        ser_buf = self._readline(timeout = 10.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not 'FT,{:s}Rsp,0]\r'.format(CMD) in ser_buf :
            return False

        return True


    # set DUT brightness, 
    # level 0...255 
    # transition is time in seconds to perform action
    def SetBrightness(self, level=100, transition=0):
        self.flushInput()
        self.write('[FT,MoveToLevelWithOnOff,{:d},{:d}]\r'.format(level, transition))

        # wait for proper response, max 200mS
        ser_buf = self._readline(timeout = 1.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not '[FT,MoveToLevelWithOnOff,0' in ser_buf :
            return None
        return ser_buf

        self.flushInput()
        # wait for response, max 8 S
        ser_buf = self._readline(timeout = 10.2)   # wait for response
        if self.verbose:
            print(ser_buf)
        if not 'FT,MoveToLevelWithOnOffRsp,0]\r' in ser_buf :
            return False

        return True
    
    # define the TXpower for the LSCT tool
    # valid range -22 ..... 0
    def SetTX_Power(self, txpower = -22):
        if txpower >= -22 and txpower <= 3 :
            self.flushInput()
            self.write('[FT,SetTxPower,{:.0f}]\r'.format(txpower))
            ser_buf = self._readline(timeout = 1.0)   # wait for response

            if self.verbose:
                print(ser_buf)

            if '[FT,SetTxPower,0' in ser_buf :     
                return True

        return False    # out of range


    # define LSCT tool sensitivity, 
    # only DUT with higher RSSI than defined and at least
    # "dist" dB stronger is accepted
    # min_level -128 .... 0
    # dist 0 .... 
    def SetRSSI_Filter(self,min_level = -128, dist = 5):
        if min_level >= -128 and min_level <= 0 :
            self.flushInput()
            self.write('[FT,SetRssiFilter,{:.0f},{:.0f}]\r'.format(min_level,dist))
            ser_buf = self._readline(timeout = 1.0)   # wait for response

            if self.verbose:
                print(ser_buf)
            
            if '[FT,SetRssiFilter,0' in ser_buf :     
                return True

        return False    # out of range


    # reset factory link tool
    # when all buffers used the get_mac will return all 00:00
    # and more nasty problems are happening
    def Tool_ResetFN(self):
        self.flushInput()
        self.write('[FT,ToolResetFN]\r')
        ser_buf = self._readline(timeout = 3.0)   # wait for response
        
        if self.verbose:
            print(ser_buf)

        # the LSCT will reboot and promp with [FT,Ready]
        # allocate serial buffer and continue
        if '[FT,Ready,0' in ser_buf :    
            if self.BoardAllocateSerialBuffer() == True :
                return True

        return False    # out of range
        


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# def testdrive():
#     print('Testdrive the factorylinktool ')
# 
#     COMPORT = 'COM38'
# 
#     # create object
#     test = FactoryLinkTool(COMPORT,
#                         timeout=0.05,
#                         baudrate=115200)
# #     if test.InitInstruments() == False :
# #         print >>sys.stderr,'Repair the Instruments !'
# #         sys.exit()
# 
# #    test.verbose = True
# #    print 'Reset FLT to factory-new'
# #    test.Tool_ResetFN()
# 
# 
#     if test.BoardAllocateSerialBuffer() == False :
#         print >>sys.stderr,'No response from Antennabox !'
#         sys.exit()
#         
#     print 'SetTX Power'    
#     if test.SetTX_Power(-21) == False :
#         print >>sys.stderr,'No proper response SetTX Power!'
#         
#     print 'Set RSSI filter'
#     if test.SetRSSI_Filter(-80,5) == False :
#         print >>sys.stderr,'No proper response Set RSSI!'
#         
#     
#     print 'BindLight'
#     if test.BindLight() == False :
#         print >>sys.stderr,'No proper response binding lamp!'
#         sys.exit()
#         
#     print 'Check for Factory New'
#     if test.CheckLightFN() == False :
#         print >>sys.stderr,'No proper response checklightFN!'
#         sys.exit()
#     
#     mac = test.GetMac()
#     if mac == None :
#         print >>sys.stderr,'Could not get MAC from lamp!'
#         sys.exit()
#     print 'Mac =  : %s'%test.MAC
# 
# #    print ''.join(str(test.MAC).split(':'))
# 
#     print 'Get Build Id Info'
#     if test.GetBuildId() == False :
#         print >>sys.stderr,'No proper response GetBuildID!'
#         sys.exit()
#     
#     test.GetLampNumber()
#     print 'lampnumber:', test.lampnumber
#     test.GetFirmwareVersion()
#     print 'firmware version:', test.firmwareversion
#     test.GetHardwareVersion()
#     print 'hardware version:', test.hardwareversion
#     test.GetModelId()
#     print 'model ID:', test.modelID
# 
#     
# 
#     for n in range (10) :
#         # set 2700K
#         print '*** 2700K'
#         test.SetBrightness(250, 2)
#         test.SetHueSat(14922,144,0)
#         time.sleep(20)
# 
#         # set red
#         print '*** RED'
#         test.SetBrightness(250, 2)
#         test.SetHueSat(0,254,0)
#         time.sleep(10)
# 
#         # set lime
#         print '*** LIME'
#         test.SetBrightness(250, 2)
#         test.SetHueSat(25600,254,0)
#         time.sleep(20)
# 
#         # set blue
#         print '*** BLUE'
#         test.SetBrightness(250, 2)
#         test.SetHueSat(47104,254,0)
#         time.sleep(20)
# 
#         # set 4000K
#         print '*** 4000K'
#         test.SetBrightness(250, 2)
#         test.SetHueSat(0,0,0)
#         time.sleep(20)




#     colors = {
#         '2700K':        '[FT,MoveToEnhancedHueAndSat,14922,144,1]',
#         '4000K':        '[FT,MoveToEnhancedHueAndSat,0,0,1]',
#         'red':          '[FT,MoveToEnhancedHueAndSat,0,254,1]',
#         'yellow':       '[FT,MoveToEnhancedHueAndSat,6400,254,1]',
#         'green/lime':   '[FT,MoveToEnhancedHueAndSat,25600,254,1]',
#         'cyan':         '[FT,MoveToEnhancedHueAndSat,33792,254,1]',
#         'blue':         '[FT,MoveToEnhancedHueAndSat,47104,254,1]',
#         'magenta':      '[FT,MoveToEnhancedHueAndSat,56320,254,1]'
#     }
#     test.SetBrightness(0, 2)
#     test.write('{:s}\r'.format(colors['4000K']))
#     ser_buf = test._readline(timeout = 1.2)   # wait for response
#     ser_buf = test._readline(timeout = 1.2)   # wait for response
#     while True:
#         test.SetBrightness(255, 2)
#         print 'ON'
# #         for color in colors:
# #             print color
# #             test.write('{:s}\r'.format(colors[color]))
# #             ser_buf = test._readline(timeout = 1.2)   # wait for response
# #             ser_buf = test._readline(timeout = 1.2)   # wait for response
# #             time.sleep(2)
# # #
#         time.sleep(5)
#         test.SetBrightness(0, 2)
#         print 'OFF'
#         time.sleep(5)


#     test.write('[FT,ReadAttr,0x1000,0x100b,0xF100]\r')
#     ret = test._readline(timeout=3)
#     print ret

#     for n in range (000,65001,1000) :
#         print 'Hue = %d'%n
#         if test.SetHueSat(n,200,0) == False :
#             print >>sys.stderr,'No proper response SetHueSat!'
#             sys.exit()
#         time.sleep(0.5)
#
#         for k in [5,10,15,20,25]:
#             test.SetBrightness(k, 2)
#             print k
#             time.sleep(0.5)

# def toolreset():
#     COMPORT = 'COM18'
# 
#     test = FactoryLinkTool(COMPORT,
#                         timeout=0.05,
#                         baudrate=115200)
# 
#     print('Allocating serial buffer')
#     if test.BoardAllocateSerialBuffer() == False :
#         print >>sys.stderr,'No response from Antennabox !'
#         sys.exit()
# 
#     print test.ToolReset()
# 
# def resettofn():
#     COMPORT = 'COM18'
# 
#     test = FactoryLinkTool(COMPORT,
#                         timeout=0.05,
#                         baudrate=115200)
# 
#     print 'Allocating serial buffer'
#     if test.BoardAllocateSerialBuffer() == False :
#         print >>sys.stderr,'No response from Antennabox !'
#         sys.exit()
# 
#     
#     print 'Binding light'
#     if test.BindLight() == False :
#         print >>sys.stderr,'No proper response binding lamp!'
#         sys.exit()
# 
#     print 'Reseting light'
#     if test.LightReset() == False:
#         print >>sys.stderr,'light reset to factory new failed'
#         sys.exit()
# 
#     if test.CheckLightFN() == False :
#         print >>sys.stderr,'No proper response checklightFN!'
#         sys.exit()
#     
#     if test.factory_new:
#         print 'device is factory new'
#         sys.exit()
#     else:
#         print 'device is not factory new'
# 
#     print 'Light reset to factory new.'
# 
# # Standalone run, without GUI !!
# if __name__ == '__main__':
# #     resettofn()
# 
#     # Actiate Relay to let JIG down
# #    relay = usbrelay.USBRelay('COM26')
# #    relay. Set_Relay(1)
#     testdrive()
# #    relay.Close_UsbRelay_Channel()
#     #toolreset()


