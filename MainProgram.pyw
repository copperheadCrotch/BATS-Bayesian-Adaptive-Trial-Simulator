# -*- coding: utf-8 -*-

# This is the main file

from PyQt4 import QtCore, QtGui
from mainwindow import Ui_MainWindow
from newSim import Ui_simulation_Frame
from newCVL import Ui_CVL_Frame
from newSimTable import Ui_Efftable_Frame
from newPatTable import Ui_Patienttable_Frame

# other module
import sys
import numpy as np
from datetime import datetime
import time
import pandas as pd

# import own module
import CVL10 as CVL
import FixedTrial as FixedTrial

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


# Main window for the application
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.newSimWindow = None
        self.newCVLWindow = None
        current_time = self.getInitTime()
        self.logConsole.setFontPointSize(11)
        self.logConsole.setTextColor(QtGui.QColor("Dark Blue"))

        # link the stdout to log textedit
        sys.stdout = StdOutStream()

        #  bind functions
        QtCore.QObject.connect(self.actionFixed_Trial_Simulation, QtCore.SIGNAL(_fromUtf8("triggered()")), self.openFixedTrialSimulation)
        QtCore.QObject.connect(self.actionCritical_Value_Lookup_Table, QtCore.SIGNAL(_fromUtf8("triggered()")), self.openCVL)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL(_fromUtf8("triggered()")), self.close)
        QtCore.QObject.connect(self.actionClear_Log, QtCore.SIGNAL(_fromUtf8("triggered()")), self.clearLog)
        QtCore.QObject.connect(sys.stdout,QtCore.SIGNAL(_fromUtf8('textWritten(QString)')),self.writeLog)

        # write start time
        sys.stdout.write("Start Time: %s\n"%(current_time))
        
    def __del__(self):
       # restore sys.stdout
       sys.stdout = sys.__stdout__
    
    # Open a new trial simulation
    def openFixedTrialSimulation(self):

        # if self.newSimWindow is None:
        #    self.newSimWindow = TrialSimWindow()
        self.newSimWindow = FixedTrialSimWindow()
        self.newSimWindow.show()
        self.logConsole.setTextColor(QtGui.QColor("Black"))
        sys.stdout.write("New task: Create a simulation with fixed allocation ratios\n")

    # open the critical value table
    def openCVL(self):

        #if self.newCVLWindow is None:
        #    self.newCVLWindow = CVLWindow()
        self.newCVLWindow = CVLWindow()
        self.newCVLWindow.show()
        self.newCVLWindow.raise_()
        self.newCVLWindow.activateWindow()
        self.logConsole.setTextColor(QtGui.QColor("Black"))
        sys.stdout.write("New task: Create a critical value look up table\n")

    # close the application
    def closeEvent(self, event):
        
        result = QtGui.QMessageBox.question(self,
                      "Quit the Application",
                      "Are you sure you want to exit?",
                      QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
        event.ignore()
        if result == QtGui.QMessageBox.Yes:

            # close all the windows
            if self.newSimWindow is not None:
                self.newSimWindow.close()
            if self.newCVLWindow is not None:
                self.newCVLWindow.close()
            event.accept()

    # write the output to log
    def writeLog(self, text):
        self.logConsole.append(text)
        
    # clear the log file
    def clearLog(self):

        # clear the log
        self.logConsole.clear()
        clear_time = self.getInitTime()
        self.logConsole.setFontPointSize(11)
        self.logConsole.setTextColor(QtGui.QColor("Dark Blue"))
        sys.stdout.write("Start Time: %s\n"%(clear_time))

    # get initial time
    def getInitTime(self):

        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return time


        
# Fixed Allocation Ratio Trial Simulation
class FixedTrialSimWindow(QtGui.QWidget, Ui_simulation_Frame):

    # Initilize
    def __init__(self, parent=None):
         
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        # Flag for arm and stage
        self.armAssigned = False
        self.stageAssigned = False
        self.Sim_objValidator = QtGui.QIntValidator(self)
        self.Sim_objValidator.setRange(1, 100000)
        self.Sim_textCtl.setValidator(self.Sim_objValidator)
        self.Seed_objValidator = QtGui.QIntValidator(self)
        self.Seed_objValidator.setRange(1,999999)
        self.Seed_textCtl.setValidator(self.Seed_objValidator)
        #self.Ful_objValidator = QtGui.QDoubleValidator(self)
        #self.Ful_objValidator.setRange(0.0,0.9,3)
        #self.Ful_objValidator.setNotation(0)
        self.Ful_objValidator = StrictDoubleValidator(self)
        self.Ful_objValidator.setRange(0.1, 0.7, 3)
        self.Ful_objValidator.setNotation(0)
        self.Ful_textCtl.setValidator(self.Ful_objValidator)
        self.Eff_objValidator = StrictDoubleValidator(self)
        self.Eff_objValidator.setRange(0.5, 0.999, 3)
        self.Eff_objValidator.setNotation(0)
        self.Eff_textCtl.setValidator(self.Eff_objValidator)
        self.ClinSig_objValidator = StrictDoubleValidator(self)
        self.ClinSig_objValidator.setRange(0.0, 0.999, 3)
        self.ClinSig_objValidator.setNotation(0)
        self.ClinSig_textCtl.setValidator(self.ClinSig_objValidator)
        self.predNum_objValidator = QtGui.QIntValidator(self)
        self.predNum_objValidator.setRange(1,1000)
        self.predNum_textCtl.setValidator(self.predNum_objValidator)
        self.predSuccess_objValidator = StrictDoubleValidator(self)
        self.predSuccess_objValidator.setRange(0.0,0.999,3)
        self.predSuccess_objValidator.setNotation(0)
        self.predSuccess_textCtl.setValidator(self.predSuccess_objValidator)

        # Binding functions
        QtCore.QObject.connect(self.nArm_comboBox, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.openEffSize)
        QtCore.QObject.connect(self.nArm_comboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.changeEffSize)
        QtCore.QObject.connect(self.nStage_comboBox, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.openPatNum)
        QtCore.QObject.connect(self.nStage_comboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.changePatNum)
        QtCore.QObject.connect(self.Seed_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.Seed_textCtl.setEnabled)
        QtCore.QObject.connect(self.predProb_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.predNum_textCtl.setEnabled)
        QtCore.QObject.connect(self.predProb_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.predSuccess_textCtl.setEnabled)
        QtCore.QObject.connect(self.predProb_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.loadCVL_checkBox.setEnabled)
        QtCore.QObject.connect(self.predProb_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.saveCVL_checkBox.setEnabled)
        
        QtCore.QObject.connect(self.loadCVL_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.loadCVL_btn.setEnabled)
        QtCore.QObject.connect(self.loadCVL_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.loadCVL_textCtl.setEnabled)
        QtCore.QObject.connect(self.loadCVL_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.saveCVL_checkBox.setDisabled)
        
        QtCore.QObject.connect(self.saveCVL_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.saveCVL_btn.setEnabled)
        QtCore.QObject.connect(self.saveCVL_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.saveCVL_textCtl.setEnabled)
        QtCore.QObject.connect(self.saveCVL_checkBox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.loadCVL_checkBox.setDisabled)
        
        QtCore.QObject.connect(self.assignEffectiveSize_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.openEffTable)
        QtCore.QObject.connect(self.assignPatient_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.openPatNumTable)
        QtCore.QObject.connect(self.loadCVL_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.loadCVL)
        QtCore.QObject.connect(self.saveCVL_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.saveCVL)
        QtCore.QObject.connect(self.runSim_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.runSim)
        QtCore.QObject.connect(self.cancelSim_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.close)


        # parameters for simulation
        # Effective Size/Treatment Effect for each group 
        self.te_list = []
        # Total Patient at each stage
        self.ts_list = []
        # Patient List
        self.ps_list = []
        # Pred List
        self.pred_list = []
        # Whether to add patients to other arms
        self.add_flag = 0
        # Predictive Probability
        self.pred_flag = 0
        # CVL file list
        self.load_file_flag = 0

    # Enable the assign effective size button    
    def openEffSize(self):

        self.armAssigned = True
        self.assignEffectiveSize_btn.setEnabled(True)

        if self.stageAssigned:

            self.assignPatient_btn.setEnabled(True)

    # Enable the assign patients button
    def openPatNum(self):

        self.stageAssigned = True
        
        if self.armAssigned:

            self.assignPatient_btn.setEnabled(True)

    def changeEffSize(self):
        
        self.numArm =  int(str(self.nArm_comboBox.currentText()))
        try:
            self.clearEffSize()
        except:
            pass
        
    def changePatNum(self):
        
        self.numStage =  int(str(self.nStage_comboBox.currentText()))
        try:
            self.clearPatNum()
        except:
            pass
        

    # opentable for effective size assignment      
    def openEffTable(self):

        """
        self.numArm =  int(str(self.nArm_comboBox.currentText()))
        # create Headers
        ColHeaders = []
        for i in range(self.numArm):
            ColHeaders.append("Arm "+str(i+1))
        self.Eff_tableWidget = EffTrialWindow()
        self.EffTable = QtGui.QTableWidget(self.Eff_tableWidget)
        #self.EffTable.setFrameStyle(QtGui.QFrame.NoFrame)
        self.EffTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.EffTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.EffTable.setRowCount(1)
        self.EffTable.setColumnCount(self.numArm)
        self.EffTable.setItemDelegate(TableDoubleValidator())
        if self.te_list:
            for j in range(self.numArm):
                if j < len(self.te_list):
                    self.EffTable.setItem(0, j, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(self.te_list[j])))
        #self.EffTable.setWidth(500)
        #self.EffTable.resize(500,75)
        self.EffTable.setHorizontalHeaderLabels(ColHeaders)
        self.EffTable.verticalHeader().setVisible(False)
        self.EffTable.verticalScrollBar().setDisabled(True)
        self.EffTable.horizontalScrollBar().setVisible(False)
        # single click to edit
        self.EffTable.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)
        layout = QtGui.QVBoxLayout(self.Eff_tableWidget)
        layout.addWidget(self.EffTable)
        layout.addWidget(self.Eff_tableWidget.saveEff_btn)
        #self.Eff_tableWidget.saveEff_btn.setEnabled(False)
        layout.addWidget(self.Eff_tableWidget.resetEff_btn)
        layout.addWidget(self.Eff_tableWidget.cancelEff_btn)
        self.Eff_tableWidget.setLayout(layout)
        self.Eff_tableWidget.show()
        """
        # self.numArm =  int(str(self.nArm_comboBox.currentText()))
        # create Headers
        self.EffColHeaders = []
        for i in range(self.numArm-1):
            self.EffColHeaders.append("Treatment "+str(i+1))
        self.EffColHeaders.append("Control")
        self.Eff_tableWidget = EffTrialWindow()
        self.EffTable = QtGui.QTableWidget(self.Eff_tableWidget)
        #self.EffTable.setFrameStyle(QtGui.QFrame.NoFrame)
        self.EffTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.EffTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.EffTable.setRowCount(1)
        self.EffTable.setColumnCount(self.numArm)
        self.EffTable.setItemDelegate(TableDoubleValidator())
        # if once opened, read the pre-specified parameter
        if self.te_list:
            for j in range(self.numArm):
                if j < len(self.te_list):
                    self.EffTable.setItem(0, j, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(self.te_list[j])))
        #self.EffTable.setWidth(500)
        #self.EffTable.resize(500,75)
        self.EffTable.setHorizontalHeaderLabels(self.EffColHeaders)
        self.EffTable.horizontalHeader().setClickable(False)
        self.EffTable.verticalHeader().setVisible(False)
        self.EffTable.verticalScrollBar().setVisible(False)
        self.EffTable.horizontalScrollBar().setVisible(False)
        # single click to edit
        self.EffTable.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        layout = QtGui.QVBoxLayout(self.Eff_tableWidget)
        hrow_btn = QtGui.QHBoxLayout(self.Eff_tableWidget)
        layout.addWidget(self.EffTable)
        hrow_btn.addWidget(self.Eff_tableWidget.saveEff_btn)
        #self.Eff_tableWidget.saveEff_btn.setEnabled(False)
        hrow_btn.addWidget(self.Eff_tableWidget.resetEff_btn)
        hrow_btn.addWidget(self.Eff_tableWidget.cancelEff_btn)
        layout.addLayout(hrow_btn)
        self.Eff_tableWidget.setLayout(layout)
        self.Eff_tableWidget.show()
        QtCore.QObject.connect(self.Eff_tableWidget.saveEff_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.saveEffSize)
        QtCore.QObject.connect(self.Eff_tableWidget.resetEff_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clearEffSize)
        QtCore.QObject.connect(self.Eff_tableWidget.cancelEff_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Eff_tableWidget.close)

    # save the effective size to a list
    def saveEffSize(self):

        self.te_list = []
        for i in range(self.numArm):
            # check if cell is empty
            # if empty, jump to the first cell that is empty
            if self.EffTable.item(0, i) is None or self.EffTable.item(0, i).text().isEmpty():
                self.msgBox = MessageBox()
                self.msgBox.setText("Effective size assignment not finished!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                #item = self.EffTable.item(0, i)
                #self.EffTable.scrollToItem(item, QtGui.QAbstractItemView.PositionAtCenter)
                self.EffTable.setCurrentCell(-1, -1)
                #self.EffTable.selectRow(0)
                #self.EffTable.selectColumn(i)
                self.EffTable.setCurrentCell(0, i)
                #self.te_list = []
                return
            else:
                self.te_list.append(float(str(self.EffTable.item(0, i).text())))
                      
        self.Eff_tableWidget.close()


    def clearEffSize(self):

        for i in range(self.numArm):
            self.EffTable.setItem(0, i, None)
        self.EffTable.setCurrentCell(-1, -1)
        self.te_list = []

    # create the widget for patients assignment
    def openPatNumTable(self):

        # get current arm and stage
        # self.numArm =  int(str(self.nArm_comboBox.currentText()))
        # self.numStage =  int(str(self.nStage_comboBox.currentText()))
        # initilize the patients assignment window
        self.Pat_tableWidget = PatNumWindow()
        self.Pat_tableWidget.setMouseTracking(True)
        # validator for allocation ratio
        self.AR_objValidator = TableARValidator(self)
        self.AR_objValidator.setRange(1.0, 5.0, 3)
        self.AR_objValidator.setNotation(0)
        self.Pat_tableWidget.allocNum_textCtl.setValidator(self.AR_objValidator)
        self.Pat_tableWidget.allocNum_textCtl.setValidator(self.AR_objValidator)
        # version 1. The number of patients is equal in all treatments
        """
        # allow users to customize the number of patients at each stage 
        # column headers
        ColHeaders = []
        for i in range(self.numArm):
            ColHeaders.append("Arm "+str(i+1))
        # row headers
        RowHeaders = []
        for j in range(self.numStage):
            RowHeaders.append("Stage "+str(j+1))
        self.PatTable = QtGui.QTableWidget(self.Pat_tableWidget)
        self.PatTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.PatTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.PatTable.setRowCount(self.numStage)
        self.PatTable.setColumnCount(self.numArm)
        self.PatTable.setItemDelegate(TableIntValidator())
        if self.ps_list:
            for k in range(self.numArm):
                for m in range(self.numStage):
                    if k < len(self.ps_array[:, 1]) and m < len(self.ps_array[1, :]):
                         self.PatTable.setItem(m, k, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(self.ps_array[k][m])))
        self.PatTable.setHorizontalHeaderLabels(ColHeaders)
        self.PatTable.setVerticalHeaderLabels(RowHeaders)
        self.PatTable.verticalScrollBar().setDisabled(True)
        self.PatTable.horizontalScrollBar().setVisible(False)
        # single click to edit
        self.PatTable.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)
        """
        # new table to show the assigned patients
        # use spin box to adjust the patients

        # Col header for total assignment table
        self.TotalColHeaders = ["Total"]
        # Row headers for total assignment table
        self.TotalRowHeaders = []
        for i in range(self.numStage):
            self.TotalRowHeaders.append("Stage "+str(i+1))
        # Col header for patient table
        self.ColHeaders = []
        for j in range(self.numArm-1):
            self.ColHeaders.append("Treatment "+str(j+1))
        self.ColHeaders.append("Control")
        # table for view of total assignment at each stage
        self.TotalPatTable = QtGui.QTableWidget(self.Pat_tableWidget)
        self.TotalPatTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.TotalPatTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.TotalPatTable.setRowCount(self.numStage)
        self.TotalPatTable.setColumnCount(1)
        self.TotalPatTable.setItemDelegate(TableIntValidator())
        self.TotalPatTable.setHorizontalHeaderLabels(self.TotalColHeaders)
        self.TotalPatTable.setVerticalHeaderLabels(self.TotalRowHeaders)
        # header not clickable
        self.TotalPatTable.verticalHeader().setClickable(False)
        self.TotalPatTable.horizontalHeader().setClickable(False)
        # scroll bar not visible
        self.TotalPatTable.verticalScrollBar().setVisible(False)
        self.TotalPatTable.horizontalScrollBar().setVisible(False)
        self.TotalPatTable.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.TotalPatTable.resizeColumnsToContents()
        # table for view of assignment
        self.PatTable = QtGui.QTableWidget(self.Pat_tableWidget)
        self.PatTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.PatTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.PatTable.setRowCount(self.numStage)
        self.PatTable.setColumnCount(self.numArm)
        # self.PatTable.setItemDelegate(TableIntValidator())
        self.PatTable.setItemDelegate(TableSpinBox())
        self.PatTable.setHorizontalHeaderLabels(self.ColHeaders)
        # self.PatTable.setVerticalHeaderLabels(RowHeaders)
        # Hide the scroll bar
        self.PatTable.verticalHeader().setVisible(False)
        self.PatTable.horizontalHeader().setClickable(False)
        self.PatTable.verticalScrollBar().setVisible(False)
        self.PatTable.horizontalScrollBar().setVisible(False)
        # self.PatTable.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        # Only read-only
        self.PatTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.PatTable.setDisabled(True)
        self.Pat_tableWidget.saveNum_btn.setDisabled(True)
        if self.add_flag == 1:
            self.Pat_tableWidget.Add_checkBox.setChecked(True)
        if self.ts_list:
            self.Pat_tableWidget.allocNum_textCtl.setText("%.3f"%(self.alloc))
            for k in range(self.numStage):
                if k < len(self.ts_list):
                    self.TotalPatTable.setItem(k, 0, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(self.ts_list[k])))
        if self.ps_list:
            self.PatTable.setDisabled(False)
            if self.numArm == len(self.ps_array[:,1]) and self.numStage == len(self.ps_array[1, :]):
                self.Pat_tableWidget.saveNum_btn.setDisabled(False)
            for m in range(self.numArm):
                for n in range(self.numStage):
                    if m < len(self.ps_array[:, 1]) and n < len(self.ps_array[1, :]):
                         self.PatTable.setItem(n, m, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(self.ps_array[m, n])))
        
        # layout 
        # allocation ratio widget
        hrow = QtGui.QHBoxLayout()
        hrow.addWidget(self.Pat_tableWidget.allocNum_label)
        hrow.addWidget(self.Pat_tableWidget.allocNum_textCtl)
        hrow.addWidget(self.Pat_tableWidget.Add_checkBox)
        htable = QtGui.QHBoxLayout()
        # htable.addWidget(self.TotalPatTable)
        # htable.addWidget(self.PatTable)
        # add a splitter
        htable_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        htable_splitter.addWidget(self.TotalPatTable)
        htable_splitter.addWidget(self.PatTable)
        # htable_splitter.setStretchFactor(1,1)
        htable_splitter.setSizes([150, 700])
        htable.addWidget(htable_splitter)
        # assign the layout
        layout = QtGui.QVBoxLayout(self.Pat_tableWidget)
        layout.addLayout(hrow)
        layout.addLayout(htable)
        #row button widget
        hrow_btn = QtGui.QHBoxLayout()
        hrow_btn.addWidget(self.Pat_tableWidget.assignNum_btn)
        hrow_btn.addWidget(self.Pat_tableWidget.saveNum_btn)
        hrow_btn.addWidget(self.Pat_tableWidget.resetNum_btn)
        hrow_btn.addWidget(self.Pat_tableWidget.cancelNum_btn)
        layout.addLayout(hrow_btn)
        """
        layout.addWidget(self.Pat_tableWidget.assignNum_btn)
        layout.addWidget(self.Pat_tableWidget.saveNum_btn)
        layout.addWidget(self.Pat_tableWidget.resetNum_btn)
        layout.addWidget(self.Pat_tableWidget.cancelNum_btn)
        """
        self.Pat_tableWidget.setLayout(layout)
        self.Pat_tableWidget.show()

        QtCore.QObject.connect(self.Pat_tableWidget.assignNum_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.assignPatNum)
        QtCore.QObject.connect(self.Pat_tableWidget.saveNum_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.savePatNum)
        QtCore.QObject.connect(self.Pat_tableWidget.resetNum_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clearPatNum)
        QtCore.QObject.connect(self.Pat_tableWidget.cancelNum_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Pat_tableWidget.close)
        QtCore.QObject.connect(self.Pat_tableWidget.allocNum_textCtl, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")),self.disableSave)
        # QtCore.QObject.connect(self.TotalPatTable, QtCore.SIGNAL(_fromUtf8("itemChanged(QTableWidgetItem*)")),self.disableSave)
        
    # assign patient number
    def assignPatNum(self):

        self.ts_list = []
        self.ps_list = []
        try:
            self.alloc = float(self.Pat_tableWidget.allocNum_textCtl.text())
            self.alloc_list = np.hstack((np.repeat(1, self.numArm-1),self.alloc))
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("Allocation ratio not specified!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            # if missing, set focus to the lineedit
            self.Pat_tableWidget.allocNum_textCtl.setFocus()
            return
        for i in range(self.numStage):
            if self.TotalPatTable.item(i, 0) is None or self.TotalPatTable.item(i, 0).text().isEmpty():
                self.msgBox = MessageBox()
                self.msgBox.setText("Patient assignment not finished!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                self.TotalPatTable.setCurrentCell(-1, -1)
                self.TotalPatTable.setCurrentCell(i, 0)
                return
            else:
                self.ts_list.append(float(str(self.TotalPatTable.item(i, 0).text())))

        # assignment of the patients based on the allocation ratio
        self.PatTable.setDisabled(False)
        self.Pat_tableWidget.saveNum_btn.setDisabled(False)
        # allocate patients
        self.temp_ps_array = np.rint(self.alloc_list.reshape(self.numArm, 1)*np.array(self.ts_list)/sum(self.alloc_list))
        self.ps_array = self.processArray(self.temp_ps_array)
        self.ps_list = self.ps_array.tolist()
        # self.ps_array = np.array(self.ps_list).reshape(self.numArm, self.numStage)
        for j in range(self.numArm):
            for k in range(self.numStage):
                # self.ps_list.append(float(str(self.PatTable.item(k, j).text())))
                self.PatTable.setItem(k, j, QtGui.QTableWidgetItem(QtCore.QString("%1").arg(self.ps_array[j][k])))
        
     
            
    # save patient number
    def savePatNum(self):

        self.ps_list = []
        # self.alloc = float(self.Pat_tableWidget.allocNum_textCtl.text())
        if self.Pat_tableWidget.Add_checkBox.isChecked():
            self.add_flag = 1
        else:
            self.add_flag = 0
        for i in range(self.numArm):
            for j in range(self.numStage):
                self.ps_list.append(float(str(self.PatTable.item(j, i).text())))
        self.ps_array = np.array(self.ps_list).reshape(self.numArm, self.numStage)
        self.Pat_tableWidget.close()
        
    # clear patient number
    def clearPatNum(self):

        self.Pat_tableWidget.Add_checkBox.setChecked(False)
        self.add_flag = 0
        for i in range(self.numStage):
            self.TotalPatTable.setItem(i, 0, None)
        self.TotalPatTable.setCurrentCell(-1, -1)
        for j in range(self.numArm):
            for k in range(self.numStage):
                self.PatTable.setItem(k, j, None)
        self.PatTable.setCurrentCell(-1, -1)
        self.ts_list = []
        self.ps_list = []
        del self.ps_array
        self.Pat_tableWidget.allocNum_textCtl.clear()
        self.PatTable.setDisabled(True)
        self.Pat_tableWidget.saveNum_btn.setDisabled(True)

    # fill the matrix
    def processArray(self, in_array):

        t_sum = np.sum(in_array, axis=0)
        for i in range(len(t_sum)):
            diff = self.ts_list[i] - t_sum[i]
            while abs(diff) != 0:
                if abs(diff) > self.numArm-1:
                    in_array[0:self.numArm, i] += 1*np.where(diff > 0, 1, -1)
                    diff -= (self.numArm-1)*np.where(diff > 0, 1, -1)
                else:
                    in_array[self.numArm-1, i] += 1*np.where(diff > 0, 1, -1)
                    diff -= 1*np.where(diff > 0, 1, -1)
                    
        return in_array

    # disable save button once changed
    def disableSave(self):

        self.Pat_tableWidget.saveNum_btn.setDisabled(True)
        
    # load CVL for posterior predictive probability 
    def loadCVL(self):
        
        self.CVLfile = str(QtGui.QFileDialog.getOpenFileName(self, 'Load CVL Table', '', self.tr("CSV(*.csv);;Pickle(*.p)")))
        # self.CVLlist = self.CVLfile.rsplit("/",1)
        # self.CVLdir = self.CVLlist[0]
        # self.CVLfilename = self.CVLlist[1]
        self.loadCVL_textCtl.setText(self.CVLfile)
        self.load_file_flag = 1

    # save the CVL file 
    def saveCVL(self):

        # convert Qstring to string
        self.CVLfile = str(QtGui.QFileDialog.getSaveFileName(self, 'Save CVL Table', '', self.tr("CSV(*.csv);;Pickle(*.p)")))
        # self.CVLlist = self.CVLfile.rsplit("/",1)
        # self.CVLdir = self.CVLlist[0]
        # self.CVLfilename = self.CVLlist[1]
        self.saveCVL_textCtl.setText(self.CVLfile)
        self.load_file_flag = -1
     
    def runSim(self):

        self.seed = -1

        try:
            self.nsim = int(self.Sim_textCtl.text())
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The number of simulations has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.Sim_textCtl.setFocus()
            return
                
        if self.Seed_checkBox.isChecked():
            try:
                self.seed = int(self.Seed_textCtl.text())
            except:
                self.msgBox = MessageBox()
                self.msgBox.setText("The seed has not been set!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                self.Seed_textCtl.setFocus()
                return

        if not self.armAssigned:
            self.msgBox = MessageBox()
            self.msgBox.setText("The number of arms has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.nArm_comboBox.setFocus()
            return

        if not self.stageAssigned:
            self.msgBox = MessageBox()
            self.msgBox.setText("The number of stage has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.nStage_comboBox.setFocus()
            return

        # if not self.te_list or self.numArm != len(self.te_list):
        if not self.te_list:
            self.msgBox = MessageBox()
            self.msgBox.setText("The treatment effect assignment has not been finished!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.assignEffectiveSize_btn.setFocus()
            return
            
        # if not self.ps_list or self.numArm*self.numStage != len(self.ps_list):
        if not self.ps_list:
            self.msgBox = MessageBox()
            self.msgBox.setText("The patients assignment has not been finished!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.assignPatient_btn.setFocus()
            return

        try:
            self.ful = float(self.Ful_textCtl.text())
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The futility boundary has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.Ful_textCtl.setFocus()
            return

        try:
            self.eff = float(self.Eff_textCtl.text())
            if self.eff <= self.ful:
                self.msgBox = MessageBox()
                self.msgBox.setText("Efficacy boundary should be larger than futility boundary!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                return
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The efficacy boundary has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.Eff_textCtl.setFocus()
            return
        
        try:
            self.clin_sig = float(self.ClinSig_textCtl.text())
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The clinically significant difference has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.ClinSig_textCtl.setFocus()
            return

        if self.predProb_checkBox.isChecked():
            self.pred_flag = 1
            try:
                self.predNum = int(self.predNum_textCtl.text())
                self.pred_list.append(predNum)
            except:
                self.msgBox = MessageBox()
                self.msgBox.setText("The patients added has not been set!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                self.predNum_textCtl.setFocus()
                return

            try:
                self.predSuccess = float(self.predSuccess_textCtl.text())
                self.pred_list.append(predSuccess)
            except:
                self.msgBox = MessageBox()
                self.msgBox.setText("The success boundary has not been set!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                self.predSuccess_textCtl.setFocus()
                return
            if self.loadCVL_checkBox.isChecked():
                if self.load_file_flag != 1:
                    self.msgBox = MessageBox()
                    self.msgBox.setText("The import table has not been set!")
                    self.msgBox.setWindowTitle("Missing Input")
                    self.msgBox.exec_()
                    self.loadCVL_btn.setFocus()
                    return
                self.pred_list.append(self.CVLfile)
            elif self.saveCVL_checkBox.isChecked():
                if self.save_file_flag != -1:
                    self.msgBox = MessageBox()
                    self.msgBox.setText("The output file is not specified!")
                    self.msgBox.setWindowTitle("Missing Input")
                    self.msgBox.exec_()
                    self.saveCVL_btn.setFocus()
                    return
                self.pred_list.append(self.CVLfile)
            self.pred_list.append(self.load_file_flag)

        # write the setting to console 
        window.logConsole.setTextColor(QtGui.QColor("Black"))
        sys.stdout.write("# of simulations:%d"%(self.nsim))
        if self.Seed_checkBox.isChecked():
            sys.stdout.write("The seed:%d"%(self.seed))
        sys.stdout.write("Effctive size:")
        sys.stdout.write(''.join(["%s\t"%colnames for colnames in self.EffColHeaders]))
        sys.stdout.write(''.join(["%.3f\t"%eff_size for eff_size in self.te_list]))
        sys.stdout.write("\nPatients of each arm at each stage:")
        df = pd.DataFrame(np.transpose(self.ps_array), index=self.TotalRowHeaders, columns=self.ColHeaders)
        sys.stdout.write(df)
        sys.stdout.write("\nFutility bounadry:%.3f"%(self.ful))
        sys.stdout.write("Efficacy boundary:%.3f"%(self.eff))
        sys.stdout.write("Clinically significant difference:%.3f"%(self.clin_sig))
        if self.predProb_checkBox.isChecked():
            sys.stdout.write("\nCalculate posterior predictive probability: Yes")
            sys.stdout.write("New patients added:%d"%self.predNum)
            sys.stdout.write("Success boundary:%.3f\n"%(self.predSuccess))
            if self.loadCVL_checkBox.isChecked():
                sys.stdout.write("Import critical lookup table from: %s"%(self.CVLfile))
            else:
                sys.stdout.write("Create a new critical lookup table")
        sys.stdout.write("Start trial simulation...")
        
        # close the window
        self.close()
 
        # call the module
        # subprocessing should be use ?
        start_time = time.time()
        FixedTrial.trial_simulation(self.nsim, self.seed, self.numArm, self.numStage,
                                    self.te_list, self.ps_array,self.alloc, self.add_flag,
                                    self.ful, self.eff,self.clin_sig, self.pred_flag,
                                    self.pred_list)
        run_time = time.time() - start_time
        
        # write the output
        
        sys.stdout.write("\nFinish trial simulation")
        sys.stdout.write("Running Time: %.3fs\n"%(run_time))

            

    # close event
    def closeEvent(self, event):

        #sys.stdout.write("Close task: Create a simulation with fixed allocation ratios\n")
        event.accept()

     
# critical value look up table created
# create a new CVL frame
class CVLWindow(QtGui.QWidget, Ui_CVL_Frame):

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.Seed_objValidator = QtGui.QIntValidator(self)
        self.Seed_objValidator.setRange(1,999999)
        self.Seed_textCtl.setValidator(self.Seed_objValidator)
        self.numPatient_objValidator = QtGui.QIntValidator(self)
        self.numPatient_objValidator.setRange(1, 1500)
        self.numPatient1_textCtl.setValidator(self.numPatient_objValidator)
        self.numPatient2_textCtl.setValidator(self.numPatient_objValidator)
        self.ClinSig_objValidator = StrictDoubleValidator(self)
        self.ClinSig_objValidator.setRange(0.0, 0.999, 3)
        self.ClinSig_objValidator.setNotation(0)
        self.outCVL_textCtl.setReadOnly(True)
        self.CVLClinSig_textCtl.setValidator(self.ClinSig_objValidator)
    
        QtCore.QObject.connect(self.outCVL_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.saveCVL)
        QtCore.QObject.connect(self.runCVL_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.runCVL)
        QtCore.QObject.connect(self.cancelCVL_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), self.close)

        self.CVLfile = ""
        self.multi_process = False

    def saveCVL(self):

        # convert Qstring to string
        self.CVLfile = str(QtGui.QFileDialog.getSaveFileName(self, 'Save CVL Table', '', self.tr("CSV(*.csv);;Pickle(*.p)")))
        # self.CVLlist = self.CVLfile.rsplit("/",1)
        # self.CVLdir = self.CVLlist[0]
        # self.CVLfilename = self.CVLlist[1]
        self.outCVL_textCtl.setText(self.CVLfile)


    def runCVL(self):

        self.seed = -1
        if self.Seed_checkBox.isChecked():
            try:
                self.seed = int(self.Seed_textCtl.text())
            except:
                self.msgBox = MessageBox()
                self.msgBox.setText("The seed has not been set!")
                self.msgBox.setWindowTitle("Missing Input")
                self.msgBox.exec_()
                self.Seed_textCtl.setFocus()
                return
        
        try:
            self.num1 = int(self.numPatient1_textCtl.text())
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The number of patients has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.numPatient1_textCtl.setFocus()
            return
        
        try:
            self.num2 = int(self.numPatient2_textCtl.text())
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The number of patients has not been set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.numPatient2_textCtl.setFocus()
            return
        
        try:
            self.clin_sig = float(self.CVLClinSig_textCtl.text())
        except:
            self.msgBox = MessageBox()
            self.msgBox.setText("The clinically sinificant difference is not set!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.CVLClinSig_textCtl.setFocus()
            return
        
        if not self.CVLfile:
            self.msgBox = MessageBox()
            self.msgBox.setText("The output file is not specified!")
            self.msgBox.setWindowTitle("Missing Input")
            self.msgBox.exec_()
            self.outCVL_btn.setFocus()
            return

        # write the setting to console 
        window.logConsole.setTextColor(QtGui.QColor("Black"))
        sys.stdout.write("Output file located in: %s"%(self.CVLfile))
        if self.Seed_checkBox.isChecked():
            sys.stdout.write("The seed:%d"%(self.seed))
        sys.stdout.write("# of patients in treatment:%d"%(self.num1))
        sys.stdout.write("# of patients in control:%d"%(self.num2))
        sys.stdout.write("Clinically significant difference:%.3f\n"%(self.clin_sig))
        sys.stdout.write("Start creating critical value look-up table...")
        # close the window
        self.close()
 
        # call the module
        # subprocessing should be use ?
        start_time = time.time()
        # start a new process
        """
        p = Process(target=CVL10.output, args=(self.seed, self.num1, self.num2, float(self.clin_sig), self.CVLfile,))
        p.start()
        p.join()
        """
        CVL.output(self.seed, self.num1, self.num2, float(self.clin_sig), self.CVLfile)
        run_time = time.time() - start_time
        
        # write the output
        
        sys.stdout.write("\nFinish creating critical value look-up table")
        sys.stdout.write("Running Time: %.3fs\n"%(run_time))
        

    def closeEvent(self, event):

        #sys.stdout.write("Run task: Create a critical value look up table\n")
        #sys.stdout.write("Close task: Create a critical value look up table\n")
        event.accept()
        


class EffTrialWindow(QtGui.QWidget, Ui_Efftable_Frame):

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

# Window for patients assignments in each arm at each stage
class PatNumWindow(QtGui.QWidget, Ui_Patienttable_Frame):

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)


class StrictDoubleValidator(QtGui.QDoubleValidator):

    def __init__(self, parent = None):

        QtGui.QDoubleValidator.__init__(self, parent)


    def validate(self, input, pos):

        state, pos = QtGui.QDoubleValidator.validate(self, input, pos)
        if input[:-1] == ".":
            return QtGui.QValidator.Intermediate, pos
        if state == QtGui.QValidator.Invalid:
            return QtGui.QValidator.Invalid, pos
        if pos == 1:
            try:
                if float(input) >= 1:
                    return QtGui.QValidator.Invalid, pos
            except:
                return QtGui.QValidator.Invalid, pos
        if pos > 1:
            try:
                if float(input) >= 1:
                    return QtGui.QValidator.Invalid, pos
            except:
                return QtGui.QValidator.Invalid, pos
        if input.isEmpty():
            return QtGui.QValidator.Intermediate, pos
        return QtGui.QValidator.Acceptable, pos


# validator for table entry
class TableDoubleValidator(QtGui.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtGui.QLineEdit(widget)
        self.cell_validator = StrictDoubleValidator(self)
        self.cell_validator.setRange(0.0, 0.999, 3)
        self.cell_validator.setNotation(0)
        self.cellEditor.setValidator(self.cell_validator)

        return self.cellEditor


# validator for allocation ratio
class TableARValidator(QtGui.QDoubleValidator):

    def __init__(self, parent = None):

        QtGui.QDoubleValidator.__init__(self, parent)


    def validate(self, input, pos):

        state, pos = QtGui.QDoubleValidator.validate(self, input, pos)
        if input[:-1] == ".":
            return QtGui.QValidator.Intermediate, pos
        if state == QtGui.QValidator.Invalid:
            return QtGui.QValidator.Invalid, pos
        if pos == 1:
            try:
                if float(input) > 6:
                    return QtGui.QValidator.Invalid, pos
            except:
                return QtGui.QValidator.Invalid, pos
        if pos > 1:
            try:
                if float(input) >= 5:
                    return QtGui.QValidator.Invalid, pos
            except:
                return QtGui.QValidator.Invalid, pos
        if input.isEmpty():
            return QtGui.QValidator.Intermediate, pos
        return QtGui.QValidator.Acceptable, pos



# Validator for patients assignments
# will be used in version 1 and version 2
class TableIntValidator(QtGui.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtGui.QLineEdit(widget)
        self.cell_validator = QtGui.QIntValidator(self)
        self.cell_validator.setRange(20, 2000)
        self.cellEditor.setValidator(self.cell_validator)
        QtCore.QObject.connect(self.cellEditor, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")),self.disableSave)

        return self.cellEditor

    def disableSave(self):

        window.newSimWindow.Pat_tableWidget.saveNum_btn.setDisabled(True)

# Spin box class for table widget
class TableSpinBox(QtGui.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtGui.QSpinBox(widget)

        return self.cellEditor


class MessageBox(QtGui.QMessageBox):

    def __init__(self, parent=None):

        QtGui.QMessageBox.__init__(self, parent)


class StdOutStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)
    """
    def __init__(self, text, parent=None):
        
        super(StdOutStream, self).__init__(parent)

        self.textWritten.emit(str(text))
    """
    def write(self, text):
        self.textWritten.emit(str(text))
        QtCore.QCoreApplication.processEvents()


        
        
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
