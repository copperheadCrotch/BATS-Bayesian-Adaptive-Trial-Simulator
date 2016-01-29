# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newPatTable.ui'
#
# Created: Wed Jan 20 10:24:15 2016
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

class Ui_Patienttable_Frame(object):
    def setupUi(self, Patienttable_Frame):
        Patienttable_Frame.setObjectName(_fromUtf8("Patienttable_Frame"))
        Patienttable_Frame.setWindowModality(QtCore.Qt.ApplicationModal)
        Patienttable_Frame.resize(850, 500)
        Patienttable_Frame.setMinimumSize(QtCore.QSize(850, 500))
        Patienttable_Frame.setMaximumSize(QtCore.QSize(850, 500))
        self.saveNum_btn = QtGui.QPushButton(Patienttable_Frame)
        self.saveNum_btn.setGeometry(QtCore.QRect(260, 310, 112, 34))
        self.saveNum_btn.setObjectName(_fromUtf8("saveNum_btn"))
        self.cancelNum_btn = QtGui.QPushButton(Patienttable_Frame)
        self.cancelNum_btn.setGeometry(QtCore.QRect(260, 410, 112, 34))
        self.cancelNum_btn.setObjectName(_fromUtf8("cancelNum_btn"))
        self.resetNum_btn = QtGui.QPushButton(Patienttable_Frame)
        self.resetNum_btn.setGeometry(QtCore.QRect(260, 360, 112, 34))
        self.resetNum_btn.setObjectName(_fromUtf8("resetNum_btn"))
        self.assignNum_btn = QtGui.QPushButton(Patienttable_Frame)
        self.assignNum_btn.setGeometry(QtCore.QRect(260, 260, 112, 34))
        self.assignNum_btn.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.assignNum_btn.setObjectName(_fromUtf8("assignNum_btn"))
        self.allocNum_label = QtGui.QLabel(Patienttable_Frame)
        self.allocNum_label.setGeometry(QtCore.QRect(20, 20, 291, 19))
        self.allocNum_label.setObjectName(_fromUtf8("allocNum_label"))
        self.allocNum_textCtl = QtGui.QLineEdit(Patienttable_Frame)
        self.allocNum_textCtl.setGeometry(QtCore.QRect(330, 20, 113, 25))
        self.allocNum_textCtl.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.allocNum_textCtl.setObjectName(_fromUtf8("allocNum_textCtl"))
        self.Add_checkBox = QtGui.QCheckBox(Patienttable_Frame)
        self.Add_checkBox.setGeometry(QtCore.QRect(470, 20, 361, 23))
        self.Add_checkBox.setObjectName(_fromUtf8("Add_checkBox"))

        self.retranslateUi(Patienttable_Frame)
        QtCore.QMetaObject.connectSlotsByName(Patienttable_Frame)
        Patienttable_Frame.setTabOrder(self.allocNum_textCtl, self.assignNum_btn)
        Patienttable_Frame.setTabOrder(self.assignNum_btn, self.saveNum_btn)
        Patienttable_Frame.setTabOrder(self.saveNum_btn, self.resetNum_btn)
        Patienttable_Frame.setTabOrder(self.resetNum_btn, self.cancelNum_btn)

    def retranslateUi(self, Patienttable_Frame):
        Patienttable_Frame.setWindowTitle(_translate("Patienttable_Frame", "Number of Patients", None))
        self.saveNum_btn.setText(_translate("Patienttable_Frame", "Save", None))
        self.cancelNum_btn.setText(_translate("Patienttable_Frame", "Cancel", None))
        self.resetNum_btn.setText(_translate("Patienttable_Frame", "Reset", None))
        self.assignNum_btn.setText(_translate("Patienttable_Frame", "Assign", None))
        self.allocNum_label.setText(_translate("Patienttable_Frame", "Allocation Ratio(Control to Treatment):", None))
        self.Add_checkBox.setText(_translate("Patienttable_Frame", "Assign Patients to Other Arms When Dropped", None))

