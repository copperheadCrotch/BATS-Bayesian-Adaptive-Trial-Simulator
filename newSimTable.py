# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newSimTable.ui'
#
# Created: Mon Jan 18 19:53:47 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Efftable_Frame(object):
    def setupUi(self, Efftable_Frame):
        Efftable_Frame.setObjectName(_fromUtf8("Efftable_Frame"))
        Efftable_Frame.setWindowModality(QtCore.Qt.ApplicationModal)
        Efftable_Frame.resize(650, 200)
        Efftable_Frame.setMaximumSize(QtCore.QSize(650, 200))
        self.saveEff_btn = QtGui.QPushButton(Efftable_Frame)
        self.saveEff_btn.setGeometry(QtCore.QRect(260, 50, 112, 34))
        self.saveEff_btn.setObjectName(_fromUtf8("saveEff_btn"))
        self.cancelEff_btn = QtGui.QPushButton(Efftable_Frame)
        self.cancelEff_btn.setGeometry(QtCore.QRect(260, 150, 112, 34))
        self.cancelEff_btn.setObjectName(_fromUtf8("cancelEff_btn"))
        self.resetEff_btn = QtGui.QPushButton(Efftable_Frame)
        self.resetEff_btn.setGeometry(QtCore.QRect(260, 100, 112, 34))
        self.resetEff_btn.setObjectName(_fromUtf8("resetEff_btn"))

        self.retranslateUi(Efftable_Frame)
        QtCore.QMetaObject.connectSlotsByName(Efftable_Frame)

    def retranslateUi(self, Efftable_Frame):
        Efftable_Frame.setWindowTitle(_translate("Efftable_Frame", "Effective Size for Each Arm", None))
        self.saveEff_btn.setText(_translate("Efftable_Frame", "Save", None))
        self.cancelEff_btn.setText(_translate("Efftable_Frame", "Cancel", None))
        self.resetEff_btn.setText(_translate("Efftable_Frame", "Reset", None))

