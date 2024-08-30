'''
Created on 26 mei 2015

@author: e.schaeffer
'''


# library imports
import configparser
import os

from PyQt5.Qt import QDialog, Qt

from gui.qt5_testmode_dialog import Ui_Dialog as UITestModeDialog  


# application imports
# test mode dialog
class TestModeDialog(QDialog, UITestModeDialog):
    parent = None

    def __init__(self, parent = None, items = []):
        QDialog.__init__(self, parent=parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowFlags(Qt.Tool | Qt.CustomizeWindowHint)
        self.show()

        self.btnSelectTestMode.clicked.connect(self.selecttestmode)
        self.listTestModes.doubleClicked.connect(self.selecttestmode)
        self.listTestModes.itemSelectionChanged.connect(self.itemselect)
        self.btnSelectTestMode.setEnabled(False)

        #self.getTestModes()
        
        self.setItems(items)


    def setItems(self, items):
        self.listTestModes.clear()
        for item in items:
            self.listTestModes.addItem(item)
                    
        
    def itemselect(self):
        enable = len(self.listTestModes.selectedIndexes()) > 0
        self.btnSelectTestMode.setEnabled(enable)


    def selecttestmode(self):
        selected = str(self.listTestModes.selectedItems()[0].text())
        self.lampfile = selected
        self.close()


