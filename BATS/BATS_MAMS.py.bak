# Import PyQt
from PyQt5 import QtGui, QtCore, QtWidgets, Qt

# Import UI
from BATS.ui.mamswindow import Ui_MAMSWindow
# Import other modules
import sys
import os
import pandas as pd
import shutil
import uuid
import numpy as np
# Cython module
import BATS.FixedTrial as FixedTrial
# Import class
# Import validator
from BATS.BATS_validator import StrictDoubleValidator
from BATS.BATS_validator import TableDoubleValidator
from BATS.BATS_validator import ContinuousValidator
from BATS.BATS_validator import StrictIntValidator
from BATS.BATS_validator import TableIntValidator
from BATS.BATS_validator import TablePriorIntValidator
from BATS.BATS_validator import TablePredIntValidator
# Import event filter
from BATS.BATS_eventfilter import WheelFilter
from BATS.BATS_eventfilter import FocusOutFilter
from BATS.BATS_eventfilter import TableFocusOutFilter
from BATS.BATS_eventfilter import HoverLeaveDocFilter
# Import messageBox
from BATS.BATS_messagebox import MessageBox



# MAMS Design Window
class MAMS_Design(QtWidgets.QWidget, Ui_MAMSWindow):


    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        # Setup ui
        self.setupUi(self)
        # Documentation dictionary
        self.doc_dict = {'sim_textCtl':'nsim', 'sim_Label':'nsim',
                    'seed_textCtl':'seed', 'seed_checkBox':'seed',
                    'nArm_Label':'narm', 'nArm_comboBox':'narm', 'trtEffSize_btn':'trteff',
                    'effSize_tableWidget':'trteff', 'prior_tableWidget':'prior',
                    'setPrior_btn':'prior', 'nStage_Label':'nstage', 'nStage_comboBox':'nstage',
                    'assignPatient_btn': 'patnum', 'setStopBoundary_btn': 'boundary',
                    'patNum_tableWidget':'patnum', 'stopBoundary_tableWidget':'boundary',
                    'predNum_tableWidget': 'predictnum',
                    'alloc_Label':'alloc', 'alloc_textCtl':'alloc',
                    'clinSig_Label':'clinicalsig', 'clinSig_textCtl':'clinicalsig',
                    'predict_checkBox':'predictprob', 'predNum_Label':'predictnum',
                    'predNum_textCtl':'predictnum', 'predNum_btn':'predictnum',
                    'predSuccess_Label':'predictsuccess','predSuccess_textCtl':'predictsuccess',
                    'predClinSig_checkBox':'predictclinicalsig','predClinSig_textCtl':'predictclinicalsig'}

        # Parent
        self.parent = parent
        # Indicate whether the test is finished. Finished: 1
        # Unfinished: 0
        self.finish_flag = 0
        self.process = None
        # Initial variable
        # Title
        self.title = "Multi-Arm Multi-Stage Design"
        # Panel
        self.panel_start = [2, 3]
        self.panel_finish = [2, 3]
        # MAMS itself
        # Number of simulations
        self.nsim = 0
        # Seed
        self.seed = 0
        # Ceresting difference
        self.clinSig = 0
        # Number of arms, number of stages, initial as 0
        self.nArm = self.nStage = 0
        # List for treatment effects, number of stages
        self.te_list = self.ns_list = []
        # Prior
        self.prior_list = []
        # Allocation ratio
        self.alloc = 0
        # Efficacy, futility
        self.eff_list = self.fut_list = []
        # Checkbox for adding patients to other treatment arms
        self.addPat = 0
        # Set predictive probability
        self.predict = 0
        # Number of new number of patients
        self.predns_list = []
        self.predSuccess = 0
        # self.predClinSig_flag = 0
        self.predClinSig = 0
        self.searchMethod = 0
        self.loadCVL = 0
        self.CVLfile = ""
        # Old settings
        self.old_setting = ()
        # Flag for treatment effect, patient assignment, prior and stopping boundaries
        self.trtEff_flag = self.patNum_flag = self.prior_flag = self.stopBoundary_flag = self.predNum_flag = True

        # Attributes
        # Flag
        self.sim_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.nArm_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.nStage_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.alloc_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.clinSig_Label.setAttribute(QtCore.Qt.WA_Hover)
        # Font
        # header font
        self.headerFont = QtGui.QFont("Segoe UI")
        self.headerFont.setPointSize(10)
        self.headerFont.setBold(False)
        # Set validator
        # Number of simulations
        self.sim_objValidator = StrictIntValidator(self)
        self.sim_objValidator.setRange(1000, 100000)
        self.sim_textCtl.setValidator(self.sim_objValidator)
        # Seed
        self.seed_objValidator = StrictIntValidator(self)
        self.seed_objValidator.setRange(1,99999)
        self.seed_textCtl.setValidator(self.seed_objValidator)
        # Clinical significant difference
        self.clinSig_objValidator = StrictDoubleValidator()
        self.clinSig_objValidator.setRange(0.0, 0.999, 3)
        self.clinSig_textCtl.setValidator(self.clinSig_objValidator)
        # Success boundary
        self.predSuccess_objValidator = StrictDoubleValidator(self)
        self.predSuccess_objValidator.setRange(0.0, 0.999, 3)
        self.predSuccess_textCtl.setValidator(self.predSuccess_objValidator)
        # Clinical significant difference for predictive probability calculation
        self.predClinSig_textCtl.setValidator(self.clinSig_objValidator)
        # self.search_comboBox.installEventFilter(self.wheelfilter)
        # Validator for allocation ratio
        self.alloc_objValidator = ContinuousValidator(self)
        self.alloc_objValidator.setRange(1.0, 4.0, 3)
        self.alloc_textCtl.setValidator(self.alloc_objValidator)
        # WheelFilter for ComboBox
        self.wheelfilter = WheelFilter()
        # FocusOut Filter for input
        self.focusOutFilter = FocusOutFilter()
        # HoverOut filter for input
        self.hoverLeaveDocFilter = HoverLeaveDocFilter()
        # FocusOut Filter for table input
        self.tableFocusOutFilter = TableFocusOutFilter()
        # Install the event filter
        self.sim_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.sim_textCtl.installEventFilter(self.focusOutFilter)
        self.sim_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.seed_checkBox.installEventFilter(self.hoverLeaveDocFilter)
        self.seed_textCtl.installEventFilter(self.focusOutFilter)
        self.seed_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.nArm_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.nArm_comboBox.installEventFilter(self.wheelfilter)
        self.nArm_comboBox.installEventFilter(self.hoverLeaveDocFilter)
        self.trtEffSize_btn.installEventFilter(self.hoverLeaveDocFilter)
        self.effSize_tableWidget.installEventFilter(self.tableFocusOutFilter)
        self.setPrior_btn.installEventFilter(self.hoverLeaveDocFilter)
        self.nStage_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.nStage_comboBox.installEventFilter(self.wheelfilter)
        self.nStage_comboBox.installEventFilter(self.hoverLeaveDocFilter)
        self.assignPatient_btn.installEventFilter(self.hoverLeaveDocFilter)
        self.setStopBoundary_btn.installEventFilter(self.hoverLeaveDocFilter)
        self.alloc_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.alloc_textCtl.installEventFilter(self.focusOutFilter)
        self.clinSig_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.alloc_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.clinSig_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.clinSig_textCtl.installEventFilter(self.focusOutFilter)
        self.predict_checkBox.installEventFilter(self.hoverLeaveDocFilter)
        self.predNum_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.predNum_btn.installEventFilter(self.hoverLeaveDocFilter)
        self.predSuccess_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.predSuccess_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.predSuccess_textCtl.installEventFilter(self.focusOutFilter)
        self.predClinSig_checkBox.installEventFilter(self.hoverLeaveDocFilter)
        self.predClinSig_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.predClinSig_textCtl.installEventFilter(self.focusOutFilter)




        # Treatment effect
        # Create headers
        self.effSize_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.effSize_tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.effSize_tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.effSize_tableWidget.setItemDelegate(TableDoubleValidator())
        self.effSize_tableWidget.horizontalHeader().setSectionsClickable(False)
        self.effSize_tableWidget.verticalHeader().setVisible(False)
        self.effSize_tableWidget.verticalScrollBar().setVisible(False)
        # Single click to edit
        self.effSize_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.trtEff_Frame.setVisible(False)

        # Patient assignment
        self.patNum_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.patNum_tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.patNum_tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.patNum_tableWidget.setItemDelegate(TableIntValidator())
        self.patNum_tableWidget.horizontalHeader().setSectionsClickable(False)
        self.patNum_tableWidget.verticalHeader().setVisible(False)
        self.patNum_tableWidget.verticalScrollBar().setVisible(False)
        self.patNum_tableWidget.horizontalScrollBar().setVisible(False)
        # Single click to edit
        self.patNum_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.patNum_Frame.setVisible(False)


        #Prior
        self.prior_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.prior_tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.prior_tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.prior_tableWidget.setItemDelegate(TablePriorIntValidator())
        self.prior_tableWidget.horizontalHeader().setSectionsClickable(False)
        self.prior_tableWidget.verticalHeader().setSectionsClickable(False)
        self.prior_tableWidget.verticalScrollBar().setVisible(False)
        # Single click to edit
        self.prior_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.prior_Frame.setVisible(False)


        # Stopping boundaries
        self.stopBoundary_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.stopBoundary_tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.stopBoundary_tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.stopBoundary_tableWidget.setItemDelegate(TableDoubleValidator())
        self.stopBoundary_tableWidget.horizontalHeader().setSectionsClickable(False)
        self.stopBoundary_tableWidget.verticalHeader().setSectionsClickable(False)
        self.stopBoundary_tableWidget.verticalScrollBar().setVisible(False)
        # Single click to edit
        self.stopBoundary_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.stopBoundary_Frame.setVisible(False)

        # Added patients
        self.predNum_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.predNum_tableWidget.horizontalHeader().setMinimumSectionSize(120)
        self.predNum_tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.predNum_tableWidget.setItemDelegate(TablePredIntValidator())
        self.predNum_tableWidget.horizontalHeader().setSectionsClickable(False)
        self.predNum_tableWidget.verticalHeader().setVisible(False)
        self.predNum_tableWidget.verticalScrollBar().setVisible(False)
        self.predNum_tableWidget.horizontalScrollBar().setVisible(False)
        # Single click to edit
        self.predNum_tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.predNum_Frame.setVisible(False)


        # Action
        # Binding functions
        self.seed_checkBox.toggled.connect(self.seed_textCtl.setEnabled)
        self.nArm_comboBox.currentIndexChanged.connect(self.setArm)
        self.nStage_comboBox.currentIndexChanged.connect(self.setStage)
        self.nArm_comboBox.currentIndexChanged.connect(self.resetEffSize)
        self.nStage_comboBox.currentIndexChanged.connect(self.resetPatNum)
        self.nArm_comboBox.currentIndexChanged.connect(self.resetPrior)
        self.nStage_comboBox.currentIndexChanged.connect(self.resetBoundary)
        self.nStage_comboBox.currentIndexChanged.connect(self.resetPredNum)
        self.predict_checkBox.toggled.connect(self.setPredict)
        self.predict_checkBox.toggled.connect(self.predSuccess_textCtl.setEnabled)
        self.predict_checkBox.toggled.connect(self.checkClinical)
        self.predict_checkBox.toggled.connect(self.checkSelected)
        self.predClinSig_checkBox.toggled.connect(self.predClinSig_textCtl.setDisabled)

        # For treatment effect
        self.trtEffSize_btn.clicked.connect(self.switchEffSize)
        self.saveEff_btn.clicked.connect(self.saveEffSize)
        self.resetEff_btn.clicked.connect(self.resetEffSize)
        self.cancelEff_btn.clicked.connect(self.switchEffSize)
        # For prior information
        self.setPrior_btn.clicked.connect(self.switchPrior)
        self.savePrior_btn.clicked.connect(self.savePrior)
        self.resetPrior_btn.clicked.connect(self.resetPrior)
        self.cancelPrior_btn.clicked.connect(self.switchPrior)
        # For patient assignment
        self.assignPatient_btn.clicked.connect(self.switchPatNum)
        self.savePat_btn.clicked.connect(self.savePatNum)
        self.resetPat_btn.clicked.connect(self.resetPatNum)
        self.cancelPat_btn.clicked.connect(self.switchPatNum)
        # For stopping boundaries assignment
        self.setStopBoundary_btn.clicked.connect(self.switchStopBoundary)
        self.saveBoundary_btn.clicked.connect(self.saveBoundary)
        self.resetBoundary_btn.clicked.connect(self.resetBoundary)
        self.cancelBoundary_btn.clicked.connect(self.switchStopBoundary)
        # For added new patients
        self.predNum_btn.clicked.connect(self.switchPredNum)
        self.savePredNum_btn.clicked.connect(self.savePredNum)
        self.resetPredNum_btn.clicked.connect(self.resetPredNum)
        self.cancelPredNum_btn.clicked.connect(self.switchPredNum)

        # Link the validator to state check
        self.sim_textCtl.textChanged.connect(self.checkEnter)
        self.seed_textCtl.textChanged.connect(self.checkEnter)
        self.alloc_textCtl.textChanged.connect(self.checkEnter)
        self.clinSig_textCtl.textChanged.connect(self.checkEnter)
        self.predSuccess_textCtl.textChanged.connect(self.checkEnter)
        self.predClinSig_textCtl.textChanged.connect(self.checkEnter)
        self.effSize_tableWidget.itemSelectionChanged.connect(self.checkTableDoc)
        self.prior_tableWidget.itemSelectionChanged.connect(self.checkTableDoc)
        self.patNum_tableWidget.itemSelectionChanged.connect(self.checkTableDoc)
        self.stopBoundary_tableWidget.itemSelectionChanged.connect(self.checkTableDoc)
        self.predNum_tableWidget.itemSelectionChanged.connect(self.checkTableDoc)
        # Link the focus out event to the check_finished_state
        self.focusOutFilter.focusOut.connect(self.checkFinishEnter)
        self.hoverLeaveDocFilter.hoverEnterDoc.connect(self.checkDoc)
        self.hoverLeaveDocFilter.hoverLeaveDoc.connect(self.checkDocOff)
        self.tableFocusOutFilter.tableFocusOut.connect(self.checkTableFinishEnter)

    # Check documentation
    def checkDoc(self, sender):

        name = str(sender.objectName())
        url = "qrc:///doc/mams/" + self.doc_dict[name] + ".html"
        self.parent.mainContent.setDoc(url)


    def checkDocOff(self, sender):

        self.parent.mainContent.clearDoc()

    
    def checkTableDoc(self):
    
        sender = self.sender()
        name = str(sender.objectName())
        url = "qrc:///doc/mams/" + self.doc_dict[name] + ".html"
        self.parent.mainContent.setDoc(url)


    # Validator function
    def checkEnter(self):

        sender = self.sender()
        if sender.text() == "":

            color = "transparent"

        else:

            validator = sender.validator()
            state = validator.validate(sender.text(), 0)[0]
            # Input is valid
            if state == QtGui.QValidator.Acceptable:

                # Check if the input are all filled, it True, send all success signal
                reciever = self.quickCheckInput()
                reciever2 = self.quickCheckValid()
                if reciever == True and reciever2 == True:

                    self.parent.mainTitle.showStatus(3)

                elif reciever2 != True:
                    
                    self.parent.mainTitle.showStatus(2, widget = reciever2)
                    
                else:

                    self.parent.mainTitle.showStatus(0, widget = reciever)

                color = '#c4df9b'

            # Warning
            elif state == QtGui.QValidator.Intermediate:

                self.parent.mainTitle.showStatus(1, sender)
                color = '#fff79a'

            # Input is not valid
            else:

                self.parent.mainTitle.showStatus(2, sender)
                color = '#ffbaba'

        sender.setStyleSheet('QLineEdit{background: %s} QLineEdit:disabled{background:#b2bbbf}' % color)

    # Validator function
    def checkFinishEnter(self, sender):

        if sender.text() == "":

            color = "transparent"

        else:

            validator = sender.validator()
            state = validator.validate(sender.text(), 0)[0]
            if state == QtGui.QValidator.Acceptable:

                # Check if the input are all filled, it True, send all success signal
                reciever = self.quickCheckInput()
                reciever2 = self.quickCheckValid()
                if reciever == True and reciever2 == True:

                    self.parent.mainTitle.showStatus(3)

                elif reciever2 != True:
                    
                    self.parent.mainTitle.showStatus(2, widget = reciever2)
                    
                else:

                    self.parent.mainTitle.showStatus(0, widget = reciever)

                color = '#c4df9b'

            # When input is focus out, check arguments
            elif state == QtGui.QValidator.Intermediate:

                self.parent.mainTitle.showStatus(2, sender)
                color = '#ffbaba' # Red

            else:

                self.parent.mainTitle.showStatus(2, sender)
                color = '#ffbaba' # Red

        sender.setStyleSheet('QLineEdit{background: %s} QLineEdit:disabled{background:#b2bbbf}' % color)


    # Check the input in the table
    def checkTableEnter(self):

        pass
            

    # Check if the input for table finiished
    def checkTableFinishEnter(self):

        pass

    # Set number of arms
    def setArm(self):

        index = self.nArm_comboBox.currentIndex()
        if index != -1:

            value = int(str(self.nArm_comboBox.currentText()))
            self.trtEffSize_btn.setEnabled(True)
            self.setPrior_btn.setEnabled(True)
            if self.nArm_comboBox.currentIndex() != -1 and value != self.nArm:

                sys.stdout.write("Selected number of  treatment arms changed from %d to %d"%(self.nArm, value))
                self.nArm = value
                # Treatment effective size set to empty: Need to reset the treatment effective size

                if self.te_list:

                    self.te_list = []
                    sys.stdout.write("Reset treatment effective size")

                if self.prior_list:

                    self.prior_list = []
                    sys.stdout.write("Reset prior information")

            elif self.nArm_comboBox.currentIndex() == -1:

                self.nArm = value
                sys.stdout.write("Selected number of treatment arms: %d" %value)


    # Set number of stages
    def setStage(self):

        index = self.nStage_comboBox.currentIndex()
        if index != -1:
            value = int(str(self.nStage_comboBox.currentText()))
            self.assignPatient_btn.setEnabled(True)
            self.setStopBoundary_btn.setEnabled(True)
            if self.nStage_comboBox.currentIndex() != -1 and value != self.nStage:

                sys.stdout.write("Selected number of stages changed from %d to %d"%(self.nStage, value))
                self.nStage = value

                if self.ns_list:

                    self.ns_list = []
                    sys.stdout.write("Reset number of patients at each stage")

                if self.fut_list:

                    self.fut_list = []
                    sys.stdout.write("Reset futility boundary")

                if self.eff_list:

                    self.eff_list = []
                    sys.stdout.write("Reset efficacy boundary")

                if self.predns_list:

                    self.predns_list = []
                    sys.stdout.write("Reset number of added patients at each stage")

            if self.predict:

                self.predNum_btn.setEnabled(True)

            elif self.nStage_comboBox.currentIndex() == -1:

                self.nStage = value
                sys.stdout.write("Selected number of stages: %d" %value)


    # Set checkbox for posterior predictive probability
    def setPredict(self):

        if self.predict_checkBox.isChecked():

            self.predict = 1
            sys.stdout.write("Set the calculation of the posterior predictive probability")

        else:

            self.predict = 0
            sys.stdout.write("Unset the calculation of the posterior predictive probability")


    # Check selected
    def checkSelected(self):

        if self.predict_checkBox.isChecked():

            if self.nStage_comboBox.currentIndex() != -1:

                self.predNum_btn.setEnabled(True)

            self.predSuccess_textCtl.setEnabled(True)
            self.predClinSig_textCtl.setEnabled(True)
            self.predClinSig_checkBox.setEnabled(True)
            if self.predClinSig_checkBox.isChecked():

                self.predClinSig_textCtl.setEnabled(False)


        else:

            self.predNum_btn.setEnabled(False)
            if not self.predNum_flag:

                self.switchPredNum()

            self.predSuccess_textCtl.setEnabled(False)
            self.predClinSig_textCtl.setEnabled(False)
            self.predClinSig_checkBox.setEnabled(False)


    # Check clinical
    def checkClinical(self):

        if self.predClinSig_checkBox.isChecked():

            self.predClinSig_textCtl.setEnabled(False)

        else:

            self.predClinSig_textCtl.setEnabled(True)


    # Switch treatment effective size frame
    def switchEffSize(self):

        if self.nArm * 80 > self.effSize_tableWidget.width():

            self.effSize_tableWidget.horizontalScrollBar().setVisible(True)

        else:

            self.effSize_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Switch function
        if self.trtEff_flag:

            self.effColHeaders = []
            for i in range(self.nArm - 1):

                self.effColHeaders.append("Treatment " + str(i + 1))

            self.effColHeaders.append("Control")
            self.effSize_tableWidget.setRowCount(1)
            self.effSize_tableWidget.setColumnCount(self.nArm)
            self.effSize_tableWidget.setCurrentCell(-1, -1)
            self.effSize_tableWidget.setHorizontalHeaderLabels(self.effColHeaders)
            # If unchanged, load the settings last time
            if self.nArm == len(self.te_list):

                for j in range(self.nArm):

                    self.effSize_tableWidget.setItem(0, j, QtWidgets.QTableWidgetItem(str(self.te_list[j])))


            self.nArm_comboBox.setEnabled(False)

        else:

            self.trtEffSize_btn.setFocus()
            self.nArm_comboBox.setEnabled(True)


        self.trtEff_Frame.setVisible(self.trtEff_flag)
        self.trtEff_flag = not self.trtEff_flag


    # Toggle for prior setting frame
    def switchPrior(self):

        # Resize the setting window
        if self.nArm * 80 > self.prior_tableWidget.width():

            self.prior_tableWidget.horizontalScrollBar().setVisible(True)

        else:

            self.prior_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Switch
        # If the prior_flag is True, then the window will open
        # If the prior_flag is False, then the window will close
        if self.prior_flag:

            self.effColHeaders = []
            for i in range(self.nArm - 1):

                self.effColHeaders.append("Treatment " + str(i + 1))

            self.effColHeaders.append("Control")
            # There are two rows, corresponding the two parameters (a, b) in Beta(a, b)
            self.prior_tableWidget.setRowCount(2)
            self.prior_tableWidget.setColumnCount(self.nArm)
            self.prior_tableWidget.setCurrentCell(-1, -1)
            self.prior_tableWidget.setHorizontalHeaderLabels(self.effColHeaders)
            self.prior_tableWidget.setVerticalHeaderLabels(["Prior A", "Prior B"])
            # If unchanged, load the settings last time
            if self.nArm == len(self.prior_list) / 2:

                for j in range(self.nArm):

                    self.prior_tableWidget.setItem(0, j, QtWidgets.QTableWidgetItem(str(int(self.prior_list[2 * j]))))
                    self.prior_tableWidget.setItem(1, j, QtWidgets.QTableWidgetItem(str(int(self.prior_list[2 * j + 1]))))

            self.nArm_comboBox.setEnabled(False)

        else:

            self.setPrior_btn.setFocus()
            self.nArm_comboBox.setEnabled(True)


        self.prior_Frame.setVisible(self.prior_flag)
        self.prior_flag = not self.prior_flag


    # Toggle for patient frame
    def switchPatNum(self):

        if self.patNum_flag:

            self.patColHeaders = []
            for i in range(self.nStage):

                self.patColHeaders.append("Stage "+str(i+1))

            self.patNum_tableWidget.setRowCount(1)
            self.patNum_tableWidget.setColumnCount(self.nStage)
            self.patNum_tableWidget.setCurrentCell(-1, -1)
            self.patNum_tableWidget.setHorizontalHeaderLabels(self.patColHeaders)

            # If unchanged, load the settings last time
            if self.nStage == len(self.ns_list):

                for j in range(self.nStage):

                    self.patNum_tableWidget.setItem(0, j, QtWidgets.QTableWidgetItem(str(int(self.ns_list[j]))))

            self.nStage_comboBox.setEnabled(False)
            self.nArm_comboBox.setEnabled(False)

        else:

            self.assignPatient_btn.setFocus()
            self.nStage_comboBox.setEnabled(True)
            self.nArm_comboBox.setEnabled(True)


        self.patNum_Frame.setVisible(self.patNum_flag)
        self.patNum_flag = not self.patNum_flag


    # Toggle for patient frame
    def switchStopBoundary(self):

        if self.stopBoundary_flag:

            self.patColHeaders = []
            for i in range(self.nStage):

                self.patColHeaders.append("Stage "+str(i+1))

            # There are two rows, corresponding to the futility and efficacy boundary
            self.stopBoundary_tableWidget.setRowCount(2)
            self.stopBoundary_tableWidget.setColumnCount(self.nStage)
            self.stopBoundary_tableWidget.setCurrentCell(-1, -1)
            self.stopBoundary_tableWidget.setHorizontalHeaderLabels(self.patColHeaders)
            self.stopBoundary_tableWidget.setVerticalHeaderLabels(["Futility", "Efficacy"])

            # If unchanged, load the settings last time
            if self.nStage == len(self.fut_list) and self.nStage == len(self.eff_list):

                for j in range(self.nStage):

                    self.stopBoundary_tableWidget.setItem(0, j, QtWidgets.QTableWidgetItem(str(self.fut_list[j])))
                    self.stopBoundary_tableWidget.setItem(1, j, QtWidgets.QTableWidgetItem(str(self.eff_list[j])))

            self.nStage_comboBox.setEnabled(False)
            self.nArm_comboBox.setEnabled(False)

        else:

            self.setStopBoundary_btn.setFocus()
            self.nStage_comboBox.setEnabled(True)
            self.nArm_comboBox.setEnabled(True)


        self.stopBoundary_Frame.setVisible(self.stopBoundary_flag)
        self.stopBoundary_flag = not self.stopBoundary_flag


    # Toggle for added patient frame
    def switchPredNum(self):

        if self.predNum_flag:

            self.patColHeaders = []
            for i in range(self.nStage):

                self.patColHeaders.append("Stage "+str(i+1))

            self.predNum_tableWidget.setRowCount(1)
            self.predNum_tableWidget.setColumnCount(self.nStage)
            self.predNum_tableWidget.setCurrentCell(-1, -1)
            self.predNum_tableWidget.setHorizontalHeaderLabels(self.patColHeaders)

            # If unchanged, load the settings last time
            if self.nStage == len(self.predns_list):

                for j in range(self.nStage):

                    self.predNum_tableWidget.setItem(0, j, QtWidgets.QTableWidgetItem(str(int(self.predns_list[j]))))

            self.nStage_comboBox.setEnabled(False)
            self.nArm_comboBox.setEnabled(False)
            self.predict_checkBox.setEnabled(False)

        else:

            self.predNum_btn.setFocus()
            self.nStage_comboBox.setEnabled(True)
            self.nArm_comboBox.setEnabled(True)
            self.predict_checkBox.setEnabled(True)

        self.predNum_Frame.setVisible(self.predNum_flag)
        self.predNum_flag = not self.predNum_flag


    # Save effective size
    def saveEffSize(self):

        self.te_list = []
        for i in range(self.nArm):

            # Check if cell is empty
            # If empty, jump to the first cell that is empty
            if self.effSize_tableWidget.item(0, i) is None or str(self.effSize_tableWidget.item(0, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("Effective size assignment not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.effSize_tableWidget.setCurrentCell(-1, -1)
                self.effSize_tableWidget.setCurrentCell(0, i)
                self.te_list = []
                return

            else:

                self.te_list.append(float(str(self.effSize_tableWidget.item(0, i).text())))

        header_string =  "Treatment arm:             \t" +  " ".join(self.effColHeaders)
        effsize_string = "Treatment effective size:\t" + "\t".join(str(te) for te in self.te_list)
        sys.stdout.write("\nSave treatment effective size\n%s"%header_string)
        sys.stdout.write(effsize_string)
        self.trtEff_flag = True
        self.trtEffSize_btn.setFocus()
        self.trtEff_Frame.setVisible(False)
        self.nArm_comboBox.setEnabled(True)


    # Reset effective size
    def resetEffSize(self):

        """
        for i in range(self.nArm):

            self.effSize_tableWidget.setItem(0, i, None)
        """
        self.effSize_tableWidget.clearContents()
        self.effSize_tableWidget.setCurrentCell(-1, -1)
        self.te_list = []
        sys.stdout.write("Reset treatment effective size")
        # self.trtEff_flag = True
        # self.trtEff_Frame.setVisible(False)


    # Save prior
    def savePrior(self):

        self.prior_list = []
        for i in range(self.nArm):

            # Check if cell is empty
            if self.prior_tableWidget.item(0, i) is None or str(self.prior_tableWidget.item(0, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("Prior distribution setting not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.prior_tableWidget.setCurrentCell(-1, -1)
                self.prior_tableWidget.setCurrentCell(0, i)
                self.prior_list = []
                return

            elif self.prior_tableWidget.item(1, i) is None or str(self.prior_tableWidget.item(1, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("Prior distribution setting not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.prior_tableWidget.setCurrentCell(-1, -1)
                self.prior_tableWidget.setCurrentCell(1, i)
                self.prior_list = []
                return

            else:

                self.prior_list.append(float(str(self.prior_tableWidget.item(0, i).text())))
                self.prior_list.append(float(str(self.prior_tableWidget.item(1, i).text())))

        header_string =  "Treatment arm:             \t" +  " ".join(self.effColHeaders)
        prior_a = [int(i) for i in self.prior_list[::2]]
        prior_b = [int(i) for i in self.prior_list[1::2]]
        prior_string = "Prior A:\t" + "\t".join(map(str, prior_a)) + "\n" + "Prior B:\t" + "\t".join(map(str, prior_b))
        # Write the information
        sys.stdout.write("\nSave prior information\n%s"%header_string)
        sys.stdout.write(prior_string)
        self.prior_flag = True
        self.setPrior_btn.setFocus()
        self.prior_Frame.setVisible(False)
        self.nArm_comboBox.setEnabled(True)


    # Reset prior
    def resetPrior(self):

        """
        for i in range(self.nArm):

            self.prior_tableWidget.setItem(0, i, None)
            self.prior_tableWidget.setItem(1, i, None)
        """
        self.prior_tableWidget.clearContents()
        self.prior_tableWidget.setCurrentCell(-1, -1)
        self.prior_list = []
        sys.stdout.write("Reset prior distribution")
        # self.prior_flag = True
        # self.prior_Frame.setVisible(False)


    # Save patient assignment
    def savePatNum(self):

        self.ns_list = []
        for i in range(self.nStage):

            # Check if cell is empty
            if self.patNum_tableWidget.item(0, i) is None or str(self.patNum_tableWidget.item(0, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("Patients assignment not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.patNum_tableWidget.setCurrentCell(-1, -1)
                self.patNum_tableWidget.setCurrentCell(0, i)
                self.ns_list = []
                return

            else:

                self.ns_list.append(float(str(self.patNum_tableWidget.item(0, i).text())))

        header_string =  "Stage:                       \t" +  " ".join(self.patColHeaders)
        patnum_string = "Number of patient:\t" + "\t".join(str(int(ns)) for ns in self.ns_list)
        sys.stdout.write("Save number of patients at each stage\n%s"%header_string)
        sys.stdout.write(patnum_string)
        self.patNum_flag = True
        self.patNum_Frame.setVisible(False)
        self.assignPatient_btn.setFocus()
        self.nArm_comboBox.setEnabled(True)
        self.nStage_comboBox.setEnabled(True)


    # Reset patient assignment
    def resetPatNum(self):

        """
        for i in range(self.nStage):

                self.patNum_tableWidget.setItem(0, i, None)
        """
        self.patNum_tableWidget.clearContents()
        self.patNum_tableWidget.setCurrentCell(-1, -1)
        self.ns_list = []
        sys.stdout.write("Reset number of patients at each stage")
        # self.patNum_flag = True
        # self.patNum_Frame.setVisible(False)


    # Save stopping boundaries
    def saveBoundary(self):

        self.fut_list = []
        self.eff_list = []
        for i in range(self.nStage):

            # Check if the futility boundary is set
            if self.stopBoundary_tableWidget.item(0, i) is None or str(self.stopBoundary_tableWidget.item(0, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("Futility boundary setting not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.stopBoundary_tableWidget.setCurrentCell(-1, -1)
                self.stopBoundary_tableWidget.setCurrentCell(0, i)
                self.fut_list = []
                self.eff_list = []
                return

            # Check if the efficacy boundary is set
            elif self.stopBoundary_tableWidget.item(1, i) is None or str(self.stopBoundary_tableWidget.item(1, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("Efficacy boundary setting not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.stopBoundary_tableWidget.setCurrentCell(-1, -1)
                self.stopBoundary_tableWidget.setCurrentCell(1, i)
                self.fut_list = []
                self.eff_list = []
                return

            else:

                self.fut_list.append(float(str(self.stopBoundary_tableWidget.item(0, i).text())))
                self.eff_list.append(float(str(self.stopBoundary_tableWidget.item(1, i).text())))

        header_string =  "Stage:                       \t" +  " ".join(self.patColHeaders)
        fut_string = "Futility Boundary:\t" + "\t".join(map(str, self.fut_list))
        eff_string = "Efficacy Boundary:\t" + "\t".join(map(str, self.eff_list))
        sys.stdout.write("Save number of patients at each stage\n%s"%header_string)
        sys.stdout.write(fut_string)
        sys.stdout.write(eff_string)
        self.stopBoundary_flag = True
        self.setStopBoundary_btn.setFocus()
        self.stopBoundary_Frame.setVisible(False)
        self.nArm_comboBox.setEnabled(True)
        self.nStage_comboBox.setEnabled(True)


    # Reset stopping boundary
    def resetBoundary(self):

        """
        for i in range(self.nStage):

            self.stopBoundary_tableWidget.setItem(0, i, None)
            self.stopBoundary_tableWidget.setItem(1, i, None)
        """
        self.stopBoundary_tableWidget.clearContents()
        self.stopBoundary_tableWidget.setCurrentCell(-1, -1)
        self.fut_list = self.eff_list = []
        sys.stdout.write("Reset stopping boundaries")
        # self.stopBoundary_flag = True
        # self.stopBoundary_Frame.setVisible(False)


    # Save patient assignment
    def savePredNum(self):

        self.predns_list = []
        for i in range(self.nStage):

            # Check if cell is empty
            if self.predNum_tableWidget.item(0, i) is None or str(self.predNum_tableWidget.item(0, i).text()) == "":

                msgBox = MessageBox()
                msgBox.setText("New patients assignment not finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.predNum_tableWidget.setCurrentCell(-1, -1)
                self.predNum_tableWidget.setCurrentCell(0, i)
                self.predns_list = []
                return

            else:

                self.predns_list.append(float(str(self.predNum_tableWidget.item(0, i).text())))

        header_string =  "Stage:                       \t" +  " ".join(self.patColHeaders)
        prednum_string = "Number of added patient:\t" + "\t".join(str(int(predns)) for predns in self.predns_list)
        sys.stdout.write("Save number of added patients at each stage\n%s"%header_string)
        sys.stdout.write(prednum_string)
        self.predNum_flag = True
        self.predNum_btn.setFocus()
        self.predNum_Frame.setVisible(False)
        self.nArm_comboBox.setEnabled(True)
        self.nStage_comboBox.setEnabled(True)
        self.predict_checkBox.setEnabled(True)


    # Reset effective size
    def resetPredNum(self):

        """
        for i in range(self.nStage):

                self.predNum_tableWidget.setItem(0, i, None)
        """
        self.predNum_tableWidget.clearContents()
        self.predNum_tableWidget.setCurrentCell(-1, -1)
        self.predns_list = []
        sys.stdout.write("Reset number of added patients at each stage")


    # Quick check if input is filled
    def quickCheckInput(self):

        if self.sim_textCtl.text() == "":

            return self.sim_textCtl

        if self.seed_checkBox.isChecked():

            if self.seed_textCtl.text() == "":

                return self.seed_textCtl

        if self.nArm_comboBox.currentIndex() == -1:

            return self.nArm_comboBox

        if not self.te_list:

            return self.trtEffSize_btn

        if not self.prior_list:

            return self.setPrior_btn

        if self.nStage_comboBox.currentIndex() == -1:

            return self.nStage_comboBox

        if not self.ns_list:

            return self.assignPatient_btn

        if not self.fut_list or not self.eff_list:

            return self.setStopBoundary_btn

        if self.alloc_textCtl.text() == "":

            return self.alloc_textCtl

        if self.clinSig_textCtl.text() == "":

            return self.clinSig_textCtl

        if self.predict_checkBox.isChecked():

            if not self.predns_list:

                return self.predNum_btn

            if self.predSuccess_textCtl.text() == "":

                return self.predSuccess_textCtl

            if self.predClinSig_checkBox.isChecked():

                if self.predClinSig_textCtl.text == "":

                    return self.predClinSig_textCtl

        return True

    def quickCheckValid(self):
 
 
         # Check the number of simulations
        # The allowed number of simulations is between 1000 and 100000
        try:

            self.nsim = int(self.sim_textCtl.text())
            if self.nsim > 100000 or self.nsim < 1000:

                return self.nsim_textCtl

        except:

            pass

        # Check the seed, if the checkbox for seed is not checked, a random seed will be used
        if self.seed_checkBox.isChecked():

            try:

                self.seed = int(self.seed_textCtl.text())
                if self.seed < 1 or self.seed > 99999:
                    
                    return self.seed_textCtl
                
            except:
                
                pass

        try:
            
            if any(prior > 5000 for prior in self.prior_list):
                 
                return self.setPrior_btn
        
        except:
            
            pass



        try:
            
            if np.sum(self.ns_list) + np.sum(self.predns_list) > 25000 :

                return self.assignPatient_btn
        
        except:
            
            pass           

        try:
            
            for i in range(0, self.nStage):

                if self.eff_list[i] < self.fut_list[i]:

                    return self.setStopBoundary_btn


        except:
            
            pass
        
        
        try:

            # Allocation ratio
            self.alloc = float(self.alloc_textCtl.text())
            if self.alloc < 1 or self.alloc > 4:
                
                return self.alloc_textCtl
            
        except:

            pass
        
        try:

            self.clinSig = float(self.clinSig_textCtl.text())
            if self.clinSig < 0 or self.clinSig >= 1:
                
                return self.clinSig_textCtl

        except:

            pass

        if self.predict_checkBox.isChecked():

            try:

                self.predSuccess = float(self.predSuccess_textCtl.text())
                if self.predSuccess < 0 or self.predSuccess > 1:
                    
                    return self.predSuccess_textCtl

            except:

                pass


            if not self.predClinSig_checkBox.isChecked():

                try:

                    self.predClinSig = float(self.predClinSig_textCtl.text())
                    if self.predClinSig < 0 or self.predClinSig > 1:
                        
                        return self.predClinSig_textCtl

                except:

                    pass

        return True


    # Run the trial
    def checkRun(self, status):

        # Check the number of simulations
        # The allowed number of simulations is between 1000 and 100000
        try:

            self.nsim = int(self.sim_textCtl.text())
            if self.nsim > 100000 or self.nsim < 1000:

                msgBox = MessageBox()
                msgBox.setText("The number of simulations should between 1000 and 100000")
                msgBox.setWindowTitle("Wrong Input")
                msgBox.exec_()
                self.sim_textCtl.setFocus()
                return

        except:

            msgBox = MessageBox()
            msgBox.setText("The number of simulations has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.sim_textCtl.setFocus()
            return

        # Check the seed, if the checkbox for seed is not checked, a random seed will be used
        if self.seed_checkBox.isChecked():

            try:

                self.seed = int(self.seed_textCtl.text())

            except:

                msgBox = MessageBox()
                msgBox.setText("The seed has not been set!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.seed_textCtl.setFocus()
                return

        else:

            self.seed = np.random.randint(1, 99999, size=1)


        # Check the number of arms
        if self.nArm_comboBox.currentIndex() == -1:

            msgBox = MessageBox()
            msgBox.setText("The number of arms has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nArm_comboBox.setFocus()
            return

        self.nArm = int(str(self.nArm_comboBox.currentText()))

        # If not self.te_list:
        if not self.te_list:

            msgBox = MessageBox()
            msgBox.setText("The treatment effect assignment has not been finished!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.trtEff_flag = True
            self.switchEffSize()
            self.effSize_tableWidget.setFocus()
            return


        # Priors
        if not self.prior_list:

            msgBox = MessageBox()
            msgBox.setText("The prior distribution has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.prior_flag = True
            self.switchPrior()
            self.prior_tableWidget.setFocus()
            return

        if any(prior > 5000 for prior in self.prior_list):

            msgBox = MessageBox()
            msgBox.setText("The prior is too large (> 5000)!")
            msgBox.setWindowTitle("Wrong Input")
            msgBox.exec_()
            self.prior_flag = True
            self.switchPrior()
            self.prior_tableWidget.setFocus()
            return

        # Check the number of stages
        if self.nStage_comboBox.currentIndex() == -1:

            msgBox = MessageBox()
            msgBox.setText("The number of stage has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nStage_comboBox.setFocus()
            return

        self.nStage = int(str(self.nStage_comboBox.currentText()))

        # If not self.ns_list
        if not self.ns_list:

            msgBox = MessageBox()
            msgBox.setText("The patients assignment has not been finished!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.patNum_flag = True
            self.switchPatNum()
            self.patNum_tableWidget.setFocus()
            return

        if np.sum(self.ns_list) + np.sum(self.predns_list) > 25000 :

            msgBox = MessageBox()
            msgBox.setText("BATS currently does not support a sample size over 25000!")
            msgBox.setWindowTitle("Wrong Input")
            msgBox.exec_()
            self.patNum_flag = True
            self.switchPatNum()
            self.patNum_tableWidget.setFocus()
            return

        # If not self.fut_list
        if not self.fut_list:

            msgBox = MessageBox()
            msgBox.setText("The futility boundary has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.stopBoundary_flag = True
            self.switchStopBoundary()
            self.stopBoundary_tableWidget.setFocus()
            return

        if not self.eff_list:

            msgBox = MessageBox()
            msgBox.setText("The efficacy boundary has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.stopBoundary_flag = True
            self.switchStopBoundary()
            self.stopBoundary_tableWidget.setFocus()
            return


        for i in range(0, self.nStage):

            if self.eff_list[i] < self.fut_list[i]:

                msgBox = MessageBox()
                msgBox.setText("Efficacy boundary at stage %d should be greater than or equal the futility boundary!"%(i + 1))
                msgBox.setWindowTitle("Wrong Input")
                msgBox.exec_()
                self.stopBoundary_flag = True
                self.switchStopBoundary()
                self.stopBoundary_tableWidget.setFocus()
                return

        try:

            # Allocation ratio
            self.alloc = float(self.alloc_textCtl.text())

        except:

            msgBox = MessageBox()
            msgBox.setText("Allocation ratio not specified!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            # If missing, set focus to the lineEdit for allocation ratio
            self.alloc_textCtl.setFocus()
            return

        try:

            self.clinSig = float(self.clinSig_textCtl.text())

        except:

            msgBox = MessageBox()
            msgBox.setText("The clinically significant difference has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.clinSig_textCtl.setFocus()
            return

        if self.predict_checkBox.isChecked():

            self.predict = 1

            if not self.predns_list:

                msgBox = MessageBox()
                msgBox.setText("The new patients assignment has not been finished!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.predNum_flag = True
                self.switchPredNum()
                self.predNum_tableWidget.setFocus()
                return

            # If all entries in new added patients are 0, only posterior probability will be used
            if self.predns_list.count(0) == self.nStage:

                msgBox = MessageBox(None, 2)
                msgBox.setText("Numbers of added patients are 0 for all stage, posterior probability will be used, do you want to continue?")
                msgBox.setWindowTitle("Warning")
                result = msgBox.exec_()
                if result:

                    pass

                else:

                    self.predNum_flag = True
                    self.switchPredNum()
                    self.predNum_tableWidget.setFocus()
                    return

            try:

                self.predSuccess = float(self.predSuccess_textCtl.text())

            except:

                msgBox = MessageBox()
                msgBox.setText("The success boundary has not been set!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.predSuccess_textCtl.setFocus()
                return


            if self.predClinSig_checkBox.isChecked():

                self.predClinSig = self.clinSig

            else:


                try:

                    self.predClinSig = float(self.predClinSig_textCtl.text())

                except:

                    msgBox = MessageBox()
                    msgBox.setText("The clinically significant difference has not been set!")
                    msgBox.setWindowTitle("Missing Input")
                    msgBox.exec_()
                    self.predClinSig_textCtl.setFocus()
                    return


        else:

            self.predict = 0
            self.predns_list = []
            self.predSuccess = 0
            self.predClinSig = 0


        if status == 1 or status == 2:
            
            msgBox = MessageBox()
            msgBox.setText("There is error in your input")
            msgBox.setWindowTitle("Wrong Input")
            msgBox.exec_()
            return


        if self.old_setting == (self.nsim, self.seed, self.nArm, self.nStage, self.te_list, self.prior_list, self.ns_list,
                                self.alloc, self.eff_list, self.fut_list,  self.clinSig,
                                self.predns_list, self.predSuccess, self.predClinSig):

            msgBox = MessageBox(None, 2)
            msgBox.setText("All the settings are the same as last run. Do you want to run it again?")
            msgBox.setWindowTitle("Run the same scenario")
            result = msgBox.exec_()
            # If return 2, continue running the scenario, if return 0, cancel this simulation
            if result:

                return 2

            else:

                return

        return 1


    # Print the settings of the run
    def printRun(self):

        self.parent.mainContent.mainContentWidget.writeConfig(config)

    # Run
    def Run(self):

        self.finish_flag = 0
        # Start thread
        try:

            # Create thread
            self.newfoldername = uuid.uuid4()
            self.pathdir = "./tmp/%s/" %self.newfoldername
            self.fullpathdir = str(os.getcwd()).replace("\\", "/") + self.pathdir[1:]
            # Main folder
            os.makedirs(self.pathdir)
            # Append to the file

            configfilename = self.pathdir + "/SimulationSetting.txt"
            trial_setting_file = open("%s/SimulationSetting.txt"%(self.pathdir), "w")
            # Write settings to the output file
            trial_setting_file.write("Simulation settings:\n")
            trial_setting_file.write("\n# of simulations: %d\n"%(self.nsim))
            if self.seed_checkBox.isChecked():

                trial_setting_file.write("The seed is set: %d\n"%(self.seed))

            else:

                trial_setting_file.write("A random seed is used: %d\n"%(self.seed))

            # Write treatment effect
            trial_setting_file.write("\nTreatment effective size:\n")
            trial_setting_file.write("\t".join(self.effColHeaders) + "\n")
            trial_setting_file.write("\t".join(map(str, self.te_list)) + "\n")
            # Write prior information
            trial_setting_file.write("\nPrior information:\n")
            trial_setting_file.write("\t" + "\t".join(self.effColHeaders) + "\n")
            trial_setting_file.write("Prior A:\t" + "\t".join(map(str, map(int, self.prior_list[::2]))) + "\n")
            trial_setting_file.write("Prior B:\t" + "\t".join(map(str, map(int, self.prior_list[1::2]))) + "\n")
            # Write patient assignment
            trial_setting_file.write("\nPatients at each stage:\n")
            trial_setting_file.write("\t".join(self.patColHeaders) + "\n")
            trial_setting_file.write("\t".join(map(str, map(int, self.ns_list))) + "\n")
            # Allocation ratio
            trial_setting_file.write("\nAllocation ratio: %.3f\n"%self.alloc)
            # Stopping boundary
            trial_setting_file.write("\nFutlity Boundary:\n")
            trial_setting_file.write("\t".join(self.patColHeaders) + "\n")
            trial_setting_file.write("\t".join(map(str, self.fut_list)) + "\n")
            trial_setting_file.write("\nEfficacy Boundary:\n")
            trial_setting_file.write("\t".join(self.patColHeaders) + "\n")
            trial_setting_file.write("\t".join(map(str, self.eff_list)) + "\n")
            # Clinically significant difference
            trial_setting_file.write("Clinically significant difference:%.3f\n"%(self.clinSig))
            if self.predict_checkBox.isChecked():

                trial_setting_file.write("\nCalculate posterior predictive probability: Yes\n")
                # Write new patient assignment
                trial_setting_file.write("\nAdded patients at each stage:\n")
                trial_setting_file.write("\t".join(self.patColHeaders) + "\n")
                trial_setting_file.write("\t".join(map(str, map(int, self.predns_list))) + "\n")
                trial_setting_file.write("Success boundary:%.3f\n"%(self.predSuccess))
                trial_setting_file.write("Clinically significant difference:%.3f\n"%(self.predClinSig))

            trial_setting_file.close()
            trial_setting_read = open(configfilename, "r")
            self.parent.mainContent.mainContentWidget.writeConfig(trial_setting_read.read())
            self.process = MAMS_Design_Thread(self.pathdir, self.effColHeaders,
                                    self.patColHeaders, self.nsim, self.seed, self.nArm, self.nStage, self.te_list, self.prior_list,
                                    self.ns_list, self.alloc, self.eff_list, self.fut_list,  self.clinSig, self.predict,
                                    self.predns_list, self.predSuccess, self.predClinSig)

            self.process.finishSignal.connect(self.Finish)
            self.process.start()

        except:

            exctype,excvalue = sys.exc_info()[:2]
            sys.stdout.write("Error: %s %s" %(str(exctype), str(excvalue)))
            shutil.rmtree(self.fullpathdir)
            self.parent.mainTitle.Finish(0)

        self.old_setting = (self.nsim, self.seed, self.nArm, self.nStage, self.te_list, self.prior_list, self.ns_list,
                            self.alloc, self.eff_list, self.fut_list,  self.clinSig,
                            self.predns_list, self.predSuccess, self.predClinSig)

    # Finish
    def Finish(self, flag):

        if flag == 0:

            self.finish_flag = 1
            sys.stdout.write("Simulation finished...")
            self.parent.mainTitle.Finish(1)

        else:

            self.finish_flag = 0
            sys.stdout.write("Oops, fail to run this simulation...")
            self.parent.mainTitle.Finish(0)
            shutil.rmtree(self.fullpathdir)

    # Reset the whole trial simulator
    def Reset(self):

        self.finish_flag = 0
        self.process = None
        # Reset all the trial settings
        self.nsim = self.seed = self.nArm = self.nStage = self.clinSig = 0
        self.sim_textCtl.clear()
        self.seed_checkBox.setChecked(False)
        self.seed_textCtl.clear()
        self.nArm_comboBox.setCurrentIndex(-1)
        self.nStage_comboBox.setCurrentIndex(-1)
        self.alloc_textCtl.clear()
        self.clinSig_textCtl.clear()
        # Reset all the predictive probabilities
        self.predict = self.predSuccess = self.predClinSig = 0
        # self.searchMethod = self.loadCVL = 0
        # self.CVLfile = ""
        self.predict_checkBox.setChecked(False)
        self.predSuccess_textCtl.clear()
        self.predClinSig_checkBox.setChecked(False)
        # self.search_comboBox.setCurrentIndex(-1)
        # self.loadCVL_checkBox.setChecked(False)
        # self.loadCVL_textCtl.clear()
        # Reset treatment effective sizes and number of patients
        if self.te_list:

            self.resetEffSize()

        if self.ns_list:

            self.resetPatNum()

        if self.prior_list:

            self.resetPrior()

        if self.fut_list or self.eff_list:

            self.resetBoundary()

        if self.predns_list:

            self.resetPredNum()

        # Set all button to be false
        self.trtEffSize_btn.setEnabled(False)
        self.setPrior_btn.setEnabled(False)
        self.assignPatient_btn.setEnabled(False)
        self.setStopBoundary_btn.setEnabled(False)
        self.predNum_btn.setEnabled(False)
        # Collapse all the opened window
        if not self.trtEff_flag:

            self.switchEffSize()

        if not self.prior_flag:

            self.switchPrior()

        if not self.patNum_flag:

            self.switchPatNum()

        if not self.stopBoundary_flag:

            self.switchStopBoundary()

        if not self.predNum_flag:

            self.switchPredNum()

    # Stop
    def Stop(self):

        sys.stdout.write("Stop MAMS simulation")
        self.process.terminate()

    # Write result to table
    def setResult(self):

        self.finalresultfile = self.fullpathdir + "/FinalResult.csv"
        self.fileindex = [0, 1]
        self.currentContent = self.parent.mainContent.mainContentWidget
        self.currentContent.setCallbackResult(self.finalresultfile, self.fileindex)

    # Write the plot
    def setPlot(self):

        self.currentContent.setCallbackPlot(self.fullpathdir)



class MAMS_Design_Thread(QtCore.QThread):


    finishSignal = QtCore.pyqtSignal(int)
    def __init__(self, pathdir, effColHeaders, patColHeaders, nsim, seed, nArm, nStage, te_list, prior_list,
                ns_list, alloc, eff_list, fut_list, clinSig, predict, predns_list, predSuccess,
                predClinSig, parent=None):

        super(MAMS_Design_Thread, self).__init__(parent)
        self.pathdir = pathdir
        self.effColHeaders = effColHeaders
        self.patColHeaders = patColHeaders
        self.nsim = nsim
        self.seed = seed
        self.nArm = nArm
        self.nStage = nStage
        self.te_list = te_list
        self.prior_list = prior_list
        self.ns_list = ns_list
        self.alloc = alloc
        self.eff_list = eff_list
        self.fut_list = fut_list
        self.clinSig = clinSig
        self.predict = predict
        self.predns_list = predns_list
        self.predSuccess = predSuccess
        self.predClinSig = predClinSig

        # Create a signal

    # Thread run function
    def run(self):

        self.finish_flag = FixedTrial.TrialSimulation(pathdir = self.pathdir, effColHeaders = self.effColHeaders, 
                                                      patColHeaders = self.patColHeaders, nsim = self.nsim, 
                                                      seed = self.seed, nArm = self.nArm, nStage = self.nStage, 
                                                      te_list = self.te_list, prior_list = self.prior_list, 
                                                      ns_list = self.ns_list, alloc = self.alloc, eff_list = self.eff_list, 
                                                      fut_list = self.fut_list, clinSig = self.clinSig, predict = self.predict, 
                                                      predns_list = self.predns_list, predSuccess = self.predSuccess, 
                                                      predClinSig = self.predClinSig)

        self.finishSignal.emit(self.finish_flag)
