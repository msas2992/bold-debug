# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\testmode_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(720, 293)
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnSelectTestMode = QtWidgets.QPushButton(Dialog)
        self.btnSelectTestMode.setObjectName("btnSelectTestMode")
        self.verticalLayout.addWidget(self.btnSelectTestMode)
        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)
        self.listTestModes = QtWidgets.QListWidget(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.listTestModes.setFont(font)
        self.listTestModes.setViewMode(QtWidgets.QListView.ListMode)
        self.listTestModes.setObjectName("listTestModes")
        self.gridLayout.addWidget(self.listTestModes, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.btnSelectTestMode.setText(_translate("Dialog", "OK"))
        self.label.setText(_translate("Dialog", "Select lamp file"))

