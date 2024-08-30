'''
Created on 20 mei 2015

@author: e.schaeffer
'''
#library imports
import csv
from datetime import datetime
import os
from pprint import pprint
import time

from PyQt5.Qt import QThread, pyqtSignal

from gui.logger import Logger
from settings import defines
from tests.maintest import TestFCTBold
from tests.test_sequence import TestSequence


class MainTestThread(QThread, Logger, TestSequence):
    bstart = False
    bstop = False
    bExitThread = False

    testmode = None
    testindex = None
    inifile = None

    setThreadFinished = pyqtSignal(int)
    textupdate = pyqtSignal(str, str)
    flagupdate = pyqtSignal(str, int)
    actionupdate = pyqtSignal(str, int)
    settingupdate = pyqtSignal(str, str)
    signalupdate = pyqtSignal(bytearray)

    def __init__(self, parent, hwsettings, outputConfig):
        QThread.__init__(self)
        TestSequence.__init__(self)
        self.parent = parent

        self.hwsettings = hwsettings
        self.outputConfig = outputConfig

        self.outputFile = None
        self.startDate = datetime.now()


    # helper methods
    def testpass(self, passfail):
        if passfail:
            self.test.values['passfail'] = 'PASS'
            self.textupdate.emit('status', 'PASS')
            self.flagupdate.emit('passfail', defines.STATUS_GREEN)
        else:
            self.test.values['passfail'] = 'FAIL'
            self.textupdate.emit('status', 'FAIL')
            self.flagupdate.emit('passfail', defines.STATUS_RED)

    def status_error(self, txt='ERROR'):
        self.textupdate.emit('status', txt)
        self.flagupdate.emit('passfail', defines.STATUS_RED)

    def testclear(self):
        self.textupdate.emit('status', 'BUSY')
        self.flagupdate.emit('passfail', defines.STATUS_CLEAR)
        self.flagupdate.emit('logclear', 0)

    def action_update(self, s, i):
        self.actionupdate.emit(s, i)

    def test_start(self):
        self.bstart = True
        self.bstop = False

    def test_stop(self):
        self.bstop = True
        self.bstart = False

    def test_finish(self):
        self.test.closeInstruments()
        self.bExitThread = True

    def setTestSettings(self, settings):
        self.test.setTestSettings(settings)

    def setBarcode(self, barcode):
        self.barcode = barcode
        self.test.barcode = self.barcode

    def csvInstrInit(self):
        self.csv = [
            datetime.now().strftime('%Y-%m-%d'),
            datetime.now().strftime('%H:%M:%S'),
            self.hwsettings.inifile,
            self.hwsettings.general['testerid']
        ]
        # TODO:

    def outputNewFile(self):
        filename = 'fct_{:s}_{:s}.csv'.format(self.barcode, self.startDate.strftime('%Y-%m-%d_%H%M'))
        self.outputFile = os.path.join(self.hwsettings.general['logdir'], filename)

    def outputSave(self):
#         pprint(self.test.values.keys())
#         for i, key in enumerate(self.test.values.keys()):
#             print('{:s} = {:d}'.format(key, i+1))

        if self.hwsettings.general['log_csv'] == False:
            return

        if self.outputFile is None:
            self.outputNewFile()

        if datetime.now().date() != self.startDate.date():
            self.startDate = datetime.now()
            self.outputNewFile()

        if not os.path.exists(self.outputFile):
            newfile = True
        else:
            newfile = False

        header = []
        values = []

        for key in sorted(self.outputConfig['keys'].keys()):
            name = self.outputConfig['keys'][key]
            if newfile:
                header.append(name)

            if name in self.test.values:
                values.append(str(self.test.values[name]))
            else:
                values.append(self.outputConfig['default'])

        with open(self.outputFile, 'at', newline='') as fd:
            writer = csv.writer(fd, delimiter=self.outputConfig['sep'])
            if len(header) > 0:
                writer.writerow(header)
            writer.writerow(values)


    # execute when self.test.start() in GUI
    def run(self):
#         self.flagupdate.emit('logclear', 0)
#         self.flagupdate.emit('passfail', defines.STATUS_CLEAR)
#         self.textupdate.emit('status', 'Initializing')

        self.log_add('creating test thread\n')
        self.test = TestFCTBold(self, self.hwsettings)
        if self.test is None:
            self.log_add('Error creating test thread')
            while True :
                self.msleep(500)
                pass

        if self.Check_Log_Folder_Exist() == False :
            self.log_add('PASS / FAIL folder problem, repair and RESTART Application ! \r')
            self.status_error()
            # wait forever, operator has to EXIT
            while True:
                self.msleep(500)
                pass

        self.log_add('Initializing instruments\n')
        # when instrument error don't start the test, notify engineer
        # and instruct to EXIT test
        ret = self.init_instruments()
        if ret == False:
            self.log_add('Instrument Error, repair and RESTART Application!\n')
            self.textupdate.emit('status', 'ERROR')
            self.flagupdate.emit('passfail', defines.STATUS_RED)
            self.status_error()
            # wait forever, operator has to EXIT
            while True:
                self.msleep(500)
                pass

        # update status text when instruments are OK
        self.textupdate.emit('status', 'Ready for test')

        self.instrument_error  = 0

        # start endless test loop, wait for jig close
        while True:
            if self.instrument_error  == 0:
                ret = self.run_test()
                if ret == True:
                    self.log_add('Test successful\r')
                    self.testpass(True)

                    # parameters define the log file name
                    self.log_save(True)
                    self.outputSave()

                elif ret == False:
                    self.log_add('Test Failed !\r')
                    if self.instrument_error  == -1:
                        self.log_add('PWM Board Communication error\n')

                    self.testpass(False)

                    # parameters define the log file name
                    self.log_save(False)
                    self.outputSave()
                else:
                    return

                # switch off voltages etc and release jig
                self.end_test()

            if self.instrument_error == -1:
                self.Reinit_Board()
