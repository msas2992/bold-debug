'''
Created on 20 mei 2015
Updates
14-09-2015 PdV Test Start string changed

@author: e.schaeffer
'''
from pprint import pprint
import time

from settings import defines
from settings.defines import Ry_Takeover


class TestSequence():
    def __init__(self):
        self.barcode = ''


    def log_header(self):
        self.time_start =  time.time()
        self.log_add('Test Software version {:s}\n'.format(defines.Version))
        self.log_add('Test started at: {:s}\n'.format(str(time.asctime(time.localtime(time.time())))))


    def log_footer(self):
        self.log_add('\nPass : ')
        self.log_add('==> Total Test time: {:.1f} sec \n'.format((time.time() - self.time_start)))

    def test_wait_for_start(self):
        # wait for test start
        self.bstart = False

        self.Deactivate_Relay(Ry_Takeover)

        self.log_add('\n\n*** Wait for barcode\n')
        self.barcode = ''
        self.flagupdate.emit('barcode', 1)
        while self.barcode == '':
            time.sleep(0.1)

        self.log_add('\n\n*** Wait for START\n')

#         if self.test.startfn is None:
#             while self.bstart == False and self.bExitThread == False:
#                 self.msleep(100)
#         else:
#             while self.test.startfn() == False:
#                 self.msleep(100)
#
#         self.bstart = False
#         self.bstop = False
#
#         if self.bExitThread:
#             return False

        # deactivate TakeOver relay


        # wait for start Idle
#         self.Print_Log('*** Wait for START button INACTIVE \r')
        while self.test.serDUT.getCTS() == True:
            time.sleep(0.1)


#         self.Print_Log('*** Wait for barcode \r')
#         while self.barcode == '':
#             time.sleep(0.1)

        # now switch is False = idle
        # wait for test start active
#         self.Print_Log('*** Wait for START button ACTIVE\r')
        while self.test.serDUT.getCTS() == False:
            time.sleep(0.1)

        self.Activate_Relay(Ry_Takeover)

        # clear user interface, e.g. status = BUSY
        self.testclear()

        # clear total logdata (printlog.py)
        self.log_clear()
        self.log_header()
        return True

    def init_instruments(self):
        self.csvInstrInit()
        for instr in self.test.instruments:
            if instr() == False:
                return False
            self.msleep(250)
        return True

    def init_settings(self):
        return self.test.init_settings()

    def run_test(self):
        if self.test_wait_for_start() == False:
            return None

        self.logClearFilenamePrefix()

        for test in self.test.tests:
            if self.bExitThread:
                return None
            if self.bstop:
                return False

            if test() == False:
                self.test.values['passfail'] = 'FAIL'

                if self.test.errorfn is not None:
                    self.test.errorfn()

                if self.test.clearfn is not None:
                    self.test.clearfn()

                return False
        return True

    def end_test(self):
        return True


    def Activate_Relay(self,port=(200,2,0)):
        self.test.instrDMM.A34907A_Digital_Output_bit(str(port[0]),
                                                      port[1],
                                                      port[2],
                                                      True)

    def Deactivate_Relay(self,port=(200,2,0)):
        self.test.instrDMM.A34907A_Digital_Output_bit(str(port[0]),
                                                      port[1],
                                                      port[2],
                                                      False)

