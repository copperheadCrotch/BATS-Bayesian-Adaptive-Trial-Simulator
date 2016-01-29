# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newCVL.ui'
#
# Created: Thu Jan 14 10:47:59 2016
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

class Ui_CVL_Frame(object):
    def setupUi(self, CVL_Frame):
        CVL_Frame.setObjectName(_fromUtf8("CVL_Frame"))
        CVL_Frame.setWindowModality(QtCore.Qt.WindowModal)
        CVL_Frame.resize(640, 400)
        CVL_Frame.setMaximumSize(QtCore.QSize(640, 400))
        CVL_Frame.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.runCVL_btn = QtGui.QPushButton(CVL_Frame)
        self.runCVL_btn.setGeometry(QtCore.QRect(380, 360, 112, 34))
        self.runCVL_btn.setObjectName(_fromUtf8("runCVL_btn"))
        self.line_6 = QtGui.QFrame(CVL_Frame)
        self.line_6.setGeometry(QtCore.QRect(-170, 340, 831, 16))
        self.line_6.setFrameShape(QtGui.QFrame.HLine)
        self.line_6.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_6.setObjectName(_fromUtf8("line_6"))
        self.cancelCVL_btn = QtGui.QPushButton(CVL_Frame)
        self.cancelCVL_btn.setGeometry(QtCore.QRect(510, 360, 112, 34))
        self.cancelCVL_btn.setObjectName(_fromUtf8("cancelCVL_btn"))
        self.outCVL_textCtl = QtGui.QLineEdit(CVL_Frame)
        self.outCVL_textCtl.setEnabled(True)
        self.outCVL_textCtl.setGeometry(QtCore.QRect(250, 290, 251, 31))
        self.outCVL_textCtl.setObjectName(_fromUtf8("outCVL_textCtl"))
        self.outCVL_btn = QtGui.QPushButton(CVL_Frame)
        self.outCVL_btn.setEnabled(True)
        self.outCVL_btn.setGeometry(QtCore.QRect(520, 290, 41, 34))
        self.outCVL_btn.setObjectName(_fromUtf8("outCVL_btn"))
        self.label = QtGui.QLabel(CVL_Frame)
        self.label.setGeometry(QtCore.QRect(100, 290, 131, 31))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_11 = QtGui.QLabel(CVL_Frame)
        self.label_11.setGeometry(QtCore.QRect(100, 240, 241, 31))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.CVLClinSig_textCtl = QtGui.QLineEdit(CVL_Frame)
        self.CVLClinSig_textCtl.setGeometry(QtCore.QRect(370, 240, 101, 31))
        self.CVLClinSig_textCtl.setObjectName(_fromUtf8("CVLClinSig_textCtl"))
        self.label_12 = QtGui.QLabel(CVL_Frame)
        self.label_12.setGeometry(QtCore.QRect(100, 140, 251, 31))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.numPatient1_textCtl = QtGui.QLineEdit(CVL_Frame)
        self.numPatient1_textCtl.setGeometry(QtCore.QRect(370, 140, 101, 31))
        self.numPatient1_textCtl.setObjectName(_fromUtf8("numPatient1_textCtl"))
        self.label_13 = QtGui.QLabel(CVL_Frame)
        self.label_13.setGeometry(QtCore.QRect(100, 190, 241, 31))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.numPatient2_textCtl = QtGui.QLineEdit(CVL_Frame)
        self.numPatient2_textCtl.setGeometry(QtCore.QRect(370, 190, 101, 31))
        self.numPatient2_textCtl.setObjectName(_fromUtf8("numPatient2_textCtl"))
        self.line_3 = QtGui.QFrame(CVL_Frame)
        self.line_3.setGeometry(QtCore.QRect(0, 60, 641, 16))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.label_5 = QtGui.QLabel(CVL_Frame)
        self.label_5.setGeometry(QtCore.QRect(20, 50, 171, 31))
        self.label_5.setAutoFillBackground(True)
        self.label_5.setFrameShape(QtGui.QFrame.Box)
        self.label_5.setFrameShadow(QtGui.QFrame.Raised)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.Seed_checkBox = QtGui.QCheckBox(CVL_Frame)
        self.Seed_checkBox.setGeometry(QtCore.QRect(270, 100, 101, 23))
        self.Seed_checkBox.setObjectName(_fromUtf8("Seed_checkBox"))
        self.Seed_textCtl = QtGui.QLineEdit(CVL_Frame)
        self.Seed_textCtl.setEnabled(False)
        self.Seed_textCtl.setGeometry(QtCore.QRect(370, 90, 101, 31))
        self.Seed_textCtl.setObjectName(_fromUtf8("Seed_textCtl"))
        self.label.setBuddy(self.outCVL_textCtl)
        self.label_11.setBuddy(self.CVLClinSig_textCtl)
        self.label_12.setBuddy(self.numPatient1_textCtl)
        self.label_13.setBuddy(self.numPatient2_textCtl)

        self.retranslateUi(CVL_Frame)
        QtCore.QObject.connect(self.Seed_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.Seed_textCtl.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(CVL_Frame)
        CVL_Frame.setTabOrder(self.Seed_checkBox, self.Seed_textCtl)
        CVL_Frame.setTabOrder(self.Seed_textCtl, self.numPatient1_textCtl)
        CVL_Frame.setTabOrder(self.numPatient1_textCtl, self.numPatient2_textCtl)
        CVL_Frame.setTabOrder(self.numPatient2_textCtl, self.CVLClinSig_textCtl)
        CVL_Frame.setTabOrder(self.CVLClinSig_textCtl, self.outCVL_textCtl)
        CVL_Frame.setTabOrder(self.outCVL_textCtl, self.outCVL_btn)
        CVL_Frame.setTabOrder(self.outCVL_btn, self.runCVL_btn)
        CVL_Frame.setTabOrder(self.runCVL_btn, self.cancelCVL_btn)

    def retranslateUi(self, CVL_Frame):
        CVL_Frame.setWindowTitle(_translate("CVL_Frame", "New Critical Value Lookup Table", None))
        self.runCVL_btn.setText(_translate("CVL_Frame", "Run", None))
        self.cancelCVL_btn.setText(_translate("CVL_Frame", "Cancel", None))
        self.outCVL_btn.setText(_translate("CVL_Frame", "...", None))
        self.label.setText(_translate("CVL_Frame", "Output Directory:", None))
        self.label_11.setText(_translate("CVL_Frame", "Clinically Significant Difference:", None))
        self.label_12.setText(_translate("CVL_Frame", "Number of Patients in Treatment:", None))
        self.label_13.setText(_translate("CVL_Frame", "Number of Patients in Control:", None))
        self.label_5.setText(_translate("CVL_Frame", "Create Table", None))
        self.Seed_checkBox.setText(_translate("CVL_Frame", "Seed:", None))

