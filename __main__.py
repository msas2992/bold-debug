'''
Created on 20 mei 2015

@author: e.schaeffer
'''
# library imports

import configparser
from glob import glob
from multiprocessing import freeze_support
import os
import sys
import fix_qt_import_error
from PyQt5.Qt import Qt, QApplication, QTextCursor, QMainWindow, QListWidgetItem, QSettings, QPixmap

from gui.qt5_mainwindow_v2b import Ui_MainWindow as MW
from gui.testmode import TestModeDialog
from tests.settings_test import SettingsTestSequence
from settings import  defines
from tests.settings_hw import SettingsGeneral
from tests.test_thread import MainTestThread
from module_locator import module_path
import subprocess, time


class TesterGui(QMainWindow, MW):
    def __init__(self, *args, **kwargs):
        # execute the constructor for QDialog
        super().__init__(*args, **kwargs)

        self.setupUi(self)
        self.setupWidgets()
        self.setupConnects()

        self.RegSettings = QSettings('PNE', 'InnoseisFCT')

        self.setWindowTitle(defines.title)

        self.restoreWindowState()
        self.show()

        self.loadConfig()

        self.scannedBarcode = None
        self.scannedBarcodeLine = ''
        self.ignoreBarcodeChanged = False

        # cmd = ['c:\\Users\\Peter\\eclipse-workspace\\PNE16-Innoseis\\files\\nodesn\\nodeSNPNE.exe', '-ln']
        # for i in range(5):
        #     try:
        #         ret = subprocess.check_output(cmd)
        #     except Exception as e:
        #         ret = str(e.output)
        #     print(ret)
        #     time.sleep(2)


    def loadConfig(self):
        self.text_update('log', 'loading settings.ini\n')
        self.config = SettingsGeneral('settings.ini')
        self.config.get_settings()

        ret = self.loadOutputConfig()
        if ret is True:
            return False

        self.loadLamps()

        self.setTestThread(MainTestThread)

    def setupWidgets(self):
        self.labelLampNumber.setText('-')
        self.labelMessage.setText('-')
        self.frameMessage.setVisible(False)
        self.labelPassFail.setText('-')

#         logo = QPixmap('files/logo/philips-hue-logo-1024x500.png').scaledToWidth(320)
#         self.labelHueLogo.setPixmap(logo)
        self.labelHueLogo.setVisible(False)
        self.labelLampUnderTest.setVisible(False)
        self.groupBox.setVisible(False)
        self.listLampTests.setVisible(False)

        self.labelDescription.setVisible(False)
        self.labelLampDescription.setVisible(False)
        self.labelLampNumber.setVisible(False)
        self.labelProductTest.setVisible(False)


    def setupConnects(self):
        self.listLampTests.itemSelectionChanged.connect(self.selectLampTest)
        self.lineBarcode.textChanged.connect(self.barcodeChanged)


    def barcodeChanged(self, text):
        if self.ignoreBarcodeChanged is True:
            return

#         if self.scannedBarcode is not None:
#             self.scannedBarcode = None
#             try:
#                 self.lineBarcode.setText(text[-1])
#             except:
#                 pass
#             self.labelLampNumber.setText('')

        if len(text) < self.config.general['barcode_length']:
            return

        self.scannedBarcodeLine = text #[0:self.config.general['barcode_length']]
        self.test.setBarcode(self.scannedBarcodeLine)
        self.ignoreBarcodeChanged = True

    def listShowLampfiles(self, lampfiles=None):
        tm = TestModeDialog(self, lampfiles)
        tm.exec_()

        items = self.listLampTests.findItems(tm.lampfile, Qt.MatchExactly)
        if len(items) == 1:
            self.setLampTest(items[0])


    def setTestThread(self, test):
        self.test = test(self, self.config, self.outputConfig)

        # connect signals
        self.test.textupdate.connect(self.text_update)
        self.test.flagupdate.connect(self.flag_update)
        self.test.signalupdate.connect(self.signal_update)
        self.btnResetCounters.clicked.connect(self.resetCounters)

        self.test.start()


    def text_update(self, field, text):
        if field == 'log':
            self.textLog.moveCursor(QTextCursor.End)
            self.textLog.insertPlainText(text)
            self.textLog.moveCursor(QTextCursor.End)
        elif field == 'status':
            self.labelPassFail.setText(text)
            if text == 'PASS':
                self.spinCounterPass.setValue(self.spinCounterPass.value() + 1)
            elif text == 'FAIL':
                self.spinCounterFail.setValue(self.spinCounterFail.value() + 1)
        else:
            # DEBUG clear signal in commandline when text wrong
            print ('*'*40)
            print (field,text)
            print ('*'*40)


    def flag_update(self, flag, val):
        if flag == 'logclear':
            self.textLog.clear()

        elif flag == 'passfail':
            if val == defines.STATUS_GREEN:
                self.labelPassFail.setStyleSheet('background-color: green;')
            elif val == defines.STATUS_RED:
                self.labelPassFail.setStyleSheet('background-color: red;')
            else:
                self.labelPassFail.setStyleSheet('background-color: white;')

        elif flag == 'barcode':
            if val == 1:
                self.lineBarcode.setText('')
                self.scannedBarcodeLine = None
                self.ignoreBarcodeChanged = False


    def signal_update(self, data):
        self.parent.signalupdate.emit(bytearray(data))


    # clear the pass / fail counters
    def resetCounters(self):
        self.spinCounterFail.setValue(0)
        self.spinCounterPass.setValue(0)


    def selectLampTest(self):
        item = self.listLampTests.currentItem()
        self.setLampTest(item)

        # ignore the barcode change event
        self.ignoreBarcodeChanged = True
        self.lineBarcode.setText('')


    def setLampTest(self, item):
        data = item.data(Qt.UserRole)
        image = data.general['image']
        img = QPixmap('files/lamps/' + image).scaledToHeight(200)
        self.labelLampUnderTest.setPixmap(img)
        self.lineBarcode.setFocus()

        self.test.setTestSettings(data)

        self.labelSettingsFilename.setText(data.inifile)
        self.labelSettingsVersion.setText(data.general['fileversion'])

        self.labelLampNumber.setText(data.inifile.split('.')[0])
        self.labelLampDescription.setText(data.general['description'])


    def restoreWindowState(self):
        self.RegSettings.beginGroup('Window')
        g = self.RegSettings.value('geometry', None)
        s = self.RegSettings.value('state', None)
        self.RegSettings.endGroup()
        if g is not None:
            self.restoreGeometry(g)
        if s is not None:
            self.restoreState(s)


    def saveWindowState(self):
        self.RegSettings.beginGroup('Window')
        self.RegSettings.setValue('geometry', self.saveGeometry())
        self.RegSettings.setValue('state', self.saveState())
        self.RegSettings.endGroup()


    def closeEvent(self, e):
        # save window state (pos,size,control values)
        self.saveWindowState()
        # exit qt application
        QMainWindow.closeEvent(self, e)

    def loadOutputConfig(self):
        inihandle = configparser.RawConfigParser()
        inihandle.read(os.path.join('files', 'csv.ini'))

        err = False
        self.text_update('log', 'loading output.ini\n')
        try:
            self.outputConfig = {
                'sep': inihandle.get('defaults', 'separator'),
                'default': inihandle.get('defaults', 'default'),
                'keys': {}
            }
        except Exception as e:
            self.text_update('log', '  error: {:s}\n'.format(str(e)))
            err = True

        for opt in inihandle.options('output'):
            try:
                index = inihandle.getint('output', opt)
            except Exception as e:
                self.text_update('log', '  error: {:s}\n'.format(str(e)))
                err = True
                continue

            if index in self.outputConfig['keys']:
                self.text_update('log', '  error: duplicate entry {:s}:{:d}\n'.format(opt, index))
                err = True
                continue

            self.outputConfig['keys'][index] = opt

        return err

    def loadLamps(self):
        lampfiles = glob('files/*.lamp')

        self.barcodes = {}
        for lf in lampfiles:
            lampfile = os.path.basename(lf)
            lampname = lampfile.split('.')[0]

            settings = SettingsTestSequence(lampfile)
            ret = settings.get_settings()
            if ret[0] is not True:
                self.text_update('log', '  error loading lamp file {:s}\n'.format(lampfile))
                continue
            self.text_update('log', 'loading lamp file {:s}\n'.format(lampfile))

            A = settings.barcode['A']
            D = settings.barcode['D']
            if A not in self.barcodes:
                self.barcodes[A] = {}
            if D in self.barcodes[A]:
                self.text_update('log',
                                 '  error possible duplicate lamp files {:s}, {:s}\n'.format(lampfile,
                                                                                             self.barcodes[A][D]))
            else:
                self.barcodes[A][D] = lampname

            item = QListWidgetItem()
            item.setText(lampname)
            item.setData(Qt.UserRole, settings)
            self.listLampTests.addItem(item)


if __name__ == '__main__':
    freeze_support()

    sys._excepthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)  # @UndefinedVariable
        sys.exit(1)
    sys.excepthook = exception_hook
    sys.stderr = open('error.txt', 'w')

    app = QApplication(sys.argv)
    # define the main_object and start
    p = TesterGui()
    # execute
    sys.exit(app.exec_())
