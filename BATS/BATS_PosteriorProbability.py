# Import PyQt
from PyQt5 import QtGui, QtCore, QtWidgets, Qt

# Import UI
from BATS.ui.posteriorprobabilitywindow import Ui_PosteriorProbabilityWindow
# Import other modules
import sys
import os
import pandas as pd
import shutil
import uuid
import numpy as np
# Cython module
import BATS.CalPosteriorProbability as CalPosteriorProbability
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
from BATS.BATS_eventfilter import HoverLeaveDocFilter
# Import messageBox
from BATS.BATS_messagebox import MessageBox


# MAMS Design Window
class PosteriorProbability_Calculation(QtWidgets.QWidget, Ui_PosteriorProbabilityWindow):
    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Setup ui
        self.setupUi(self)
        # Documentation dictionary
        self.doc_dict = {'nSuccessTrt_Label':'posterior', 'nSuccessTrt_textCtl':'posterior', 
                    'nFailTrt_Label':'posterior', 'nFailTrt_textCtl':'posterior', 
                    'nSuccessControl_Label':'posterior', 'nSuccessControl_textCtl':'posterior', 
                    'nFailControl_Label':'posterior', 'nFailControl_textCtl':'posterior', 
                    'trtPrior_Label':'prior', 'trtPriorA_textCtl': 'prior', 'trtPriorB_textCtl':'prior',
                    'controlPrior_Label':'prior', 'controlPriorA_textCtl':'prior', 
                    'controlPriorB_textCtl':'prior','clinSig_Label':'clinicalsig', 
                    'clinSig_textCtl':'clinicalsig','seed_checkBox':'seed', 'seed_textCtl':'seed'}
        # Parent
        self.parent = parent
        # Indicate whether the test is finished. Finished: 1
        # Unfinished: 0
        self.finish_flag = 0
        self.process = None
        # Initial variable
        # Title
        self.title = "Posterior Probability Calculation"       
        # Panel
        self.panel_start = [2, 3]
        self.panel_finish = []
        
        # PosteriorProbability itself
        # Treatment success
        self.nsTrt = 0
        self.nfTrt = 0
        # Control success
        self.nsControl = 0
        self.nfControl = 0
        # Prior
        self.prioraTrt = 0
        self.priorbTrt = 0
        self.prioraControl = 0
        self.priorbControl = 0
        # Seed
        self.seed = 0
        # Ceresting difference
        self.clinSig = 0
        # Old settings
        self.old_setting = ()
        
        
        # Attributes
        # Flag
        self.nSuccessTrt_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.nFailTrt_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.nSuccessControl_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.nFailControl_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.trtPrior_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.trtPriorA_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.trtPriorB_Label.setAttribute(QtCore.Qt.WA_Hover)     
        self.controlPrior_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.controlPriorA_Label.setAttribute(QtCore.Qt.WA_Hover)
        self.controlPriorB_Label.setAttribute(QtCore.Qt.WA_Hover)     
        self.clinSig_Label.setAttribute(QtCore.Qt.WA_Hover)
        
        # Treatment
        self.number_objValidator = StrictIntValidator(self)
        self.number_objValidator.setRange(1, 20000)
        self.nSuccessTrt_textCtl.setValidator(self.number_objValidator)
        self.nFailTrt_textCtl.setValidator(self.number_objValidator)   
        self.nSuccessControl_textCtl.setValidator(self.number_objValidator)
        self.nFailControl_textCtl.setValidator(self.number_objValidator)        
        # Prior 
        self.prior_objValidator = StrictIntValidator(self)
        self.prior_objValidator.setRange(1, 5000)
        self.trtPriorA_textCtl.setValidator(self.prior_objValidator)
        self.trtPriorB_textCtl.setValidator(self.prior_objValidator)
        self.controlPriorA_textCtl.setValidator(self.prior_objValidator)
        self.controlPriorB_textCtl.setValidator(self.prior_objValidator)
        
        
        # Seed
        self.seed_objValidator = StrictIntValidator(self)
        self.seed_objValidator.setRange(1,99999)
        self.seed_textCtl.setValidator(self.seed_objValidator)
        # Clinical significant difference
        self.clinSig_objValidator = StrictDoubleValidator()
        self.clinSig_objValidator.setRange(0.0, 0.999, 3)
        self.clinSig_textCtl.setValidator(self.clinSig_objValidator)   

        # FocusOut Filter for input
        self.focusOutFilter = FocusOutFilter()
        # HoverOut filter for input
        self.hoverLeaveDocFilter = HoverLeaveDocFilter()
        
        
        self.nSuccessTrt_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.nSuccessTrt_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.nSuccessTrt_textCtl.installEventFilter(self.focusOutFilter)
        self.nFailTrt_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.nFailTrt_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.nFailTrt_textCtl.installEventFilter(self.focusOutFilter)
        self.trtPrior_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.trtPriorA_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.trtPriorA_textCtl.installEventFilter(self.focusOutFilter)
        self.trtPriorB_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.trtPriorB_textCtl.installEventFilter(self.focusOutFilter)
        self.nSuccessControl_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.nSuccessControl_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.nSuccessControl_textCtl.installEventFilter(self.focusOutFilter)
        self.nFailControl_Label.installEventFilter(self.hoverLeaveDocFilter)
        self.nFailControl_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.nFailControl_textCtl.installEventFilter(self.focusOutFilter)
        self.controlPrior_Label.installEventFilter(self.hoverLeaveDocFilter)   
        self.controlPriorA_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.controlPriorA_textCtl.installEventFilter(self.focusOutFilter)
        self.controlPriorB_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.controlPriorB_textCtl.installEventFilter(self.focusOutFilter)     
        self.clinSig_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        self.clinSig_textCtl.installEventFilter(self.focusOutFilter)    
        self.seed_checkBox.installEventFilter(self.hoverLeaveDocFilter)
        self.seed_textCtl.installEventFilter(self.focusOutFilter)
        self.seed_textCtl.installEventFilter(self.hoverLeaveDocFilter)
        
        
        # Signal
        self.seed_checkBox.toggled.connect(self.seed_textCtl.setEnabled)
        
        self.nSuccessTrt_textCtl.textChanged.connect(self.checkEnter)
        self.nFailTrt_textCtl.textChanged.connect(self.checkEnter)
        self.trtPriorA_textCtl.textChanged.connect(self.checkEnter)
        self.trtPriorB_textCtl.textChanged.connect(self.checkEnter)
        self.nSuccessControl_textCtl.textChanged.connect(self.checkEnter)
        self.nFailControl_textCtl.textChanged.connect(self.checkEnter)
        self.controlPriorA_textCtl.textChanged.connect(self.checkEnter)
        self.controlPriorB_textCtl.textChanged.connect(self.checkEnter)
        self.seed_textCtl.textChanged.connect(self.checkEnter)
        self.clinSig_textCtl.textChanged.connect(self.checkEnter)
        # Link the focus out event to the check_finished_state
        self.focusOutFilter.focusOut.connect(self.checkFinishEnter)
        self.hoverLeaveDocFilter.hoverEnterDoc.connect(self.checkDoc)
        self.hoverLeaveDocFilter.hoverLeaveDoc.connect(self.checkDocOff)    
        
        
    # Check documentation
    def checkDoc(self, sender):
        
        name = str(sender.objectName())
        url = "qrc:///doc/posteriorprob/" + self.doc_dict[name] + ".html"
        self.parent.mainContent.setDoc(url)
        
    
    def checkDocOff(self, sender):
        
        self.parent.mainContent.clearDoc()
        
      
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
        
        
    # Quick check if input is filled
    def quickCheckInput(self):
        
        
        if self.nSuccessTrt_textCtl.text() == "":
            
            return self.nSuccessTrt_textCtl
        
        if self.nFailTrt_textCtl.text() == "":
            
            return self.nFailTrt_textCtl
        
        if self.trtPriorA_textCtl.text() == "":
            
            return self.trtPriorA_textCtl
            
        if self.trtPriorB_textCtl.text() == "":
            
            return self.trtPriorB_textCtl        
        
        if self.nSuccessControl_textCtl.text() == "":
            
            return self.nSuccessControl_textCtl
        
        if self.nFailControl_textCtl.text() == "":
            
            return self.nFailControl_textCtl
        
        if self.controlPriorA_textCtl.text() == "":
            
            return self.controlPriorA_textCtl
            
        if self.controlPriorB_textCtl.text() == "":
            
            return self.controlPriorB_textCtl   
        
        if self.clinSig_textCtl.text() == "":
            
            return self.clinSig_textCtl
        
        if self.seed_checkBox.isChecked():
            
            if self.seed_textCtl.text() == "":
                
                return self.seed_textCtl
        
        return True        
     


    # Run the trial
    def quickCheckValid(self):
        
        # Check the number of simulations
        try:
            
            self.nsTrt = int(self.nSuccessTrt_textCtl.text())
            if self.nsTrt < 1 or self.nsTrt > 20000:
                
                return self.nSuccessTrt_textCtl
                
        except:
            
            pass

        try:
            
            self.nfTrt = int(self.nFailTrt_textCtl.text())
            if self.nfTrt < 1 or self.nfTrt > 20000:
                
                return self.nFailTrt_textCtl    
        
        except:
            
            pass     

        try:
            
            self.nsControl = int(self.nSuccessControl_textCtl.text())
            if self.nsControl < 1 or self.nsControl > 20000:
                
                return self.nsControl_textCtl
                    
        except:
            
            pass
            
        try:
            
            self.nfControl = int(self.nFailControl_textCtl.text())
            if self.nfControl < 1 or self.nfControl > 20000:
                
                return self.nfControl_textCtl        
        except:
            
            pass
 
 
        try:
            
            self.prioraTrt = int(self.trtPriorA_textCtl.text())
            if self.prioraTrt < 1 or self.prioraTrt > 5000:
                
                return self.trtPriorA_textCtl
        
        except:
            
            pass
        
        
        try:
            
            self.priorbTrt = int(self.trtPriorB_textCtl.text())
            if self.priorbTrt < 1 or self.priorbTrt > 5000:
                
                return self.trtPriorB_textCtl
        
        except:
            
            pass

        try:
            
            self.prioraControl = int(self.controlPriorA_textCtl.text())
            if self.prioraControl < 1 or self.prioraControl > 5000:
                
                return self.controlPriorA_textCtl
        
        except:
            
            pass

        try:
            
            self.priorbControl = int(self.controlPriorB_textCtl.text())
            if self.priorbControl < 1 or self.priorbControl > 5000:
                
                return self.controlPriorB_textCtl
        
        except:
            
            pass     
        
        # Check the seed, if the checkbox for seed is not checked, a random seed will be used
        if self.seed_checkBox.isChecked():
            
            try:
            
                self.seed = int(self.seed_textCtl.text())
                if self.seed < 0 or self.seed > 99999:
                    
                    return self.seed_textCtl
            
            except:
            
                pass
        
        try:
            
            self.clinSig = float(self.clinSig_textCtl.text())
            if self.clinSig < 0 or self.clinSig >= 1:
                
                return self.clinSig_textCtl
        
        except:
        
            pass

        
        return True



    # Run the trial
    def checkRun(self, status):
        
        # Check the number of simulations
        # The allowed number of simulations is between 1000 and 100000
        try:
            
            self.nsTrt = int(self.nSuccessTrt_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The number of success in treatment has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nSuccessTrt_textCtl.setFocus()
            return

        try:
            
            self.nfTrt = int(self.nFailTrt_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The number of failure in treatment has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nFailTrt_textCtl.setFocus()
            return        

        try:
            
            self.nsControl = int(self.nSuccessControl_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The number of success in control has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nSuccessControl_textCtl.setFocus()
            return
            
        try:
            
            self.nfControl = int(self.nFailControl_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The number of failure in control has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nFailControl_textCtl.setFocus()
            return
 
 
        try:
            
            self.prioraTrt = int(self.trtPriorA_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The prior of treatment has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.trtPriorA_textCtl.setFocus()
            return   
            
            
 
        try:
            
            self.priorbTrt = int(self.trtPriorB_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The prior of treatment has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.trtPriorB_textCtl.setFocus()
            return   


        try:
            
            self.prioraControl = int(self.controlPriorA_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The prior of control has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.controlPriorA_textCtl.setFocus()
            return   
            
            
        try:
            
            self.priorbControl = int(self.controlPriorB_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The prior of control has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.controlPriorB_textCtl.setFocus()
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


        try:
            
            self.clinSig = float(self.clinSig_textCtl.text())
        
        except:
        
            msgBox = MessageBox()
            msgBox.setText("The clinically significant difference has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.clinSig_textCtl.setFocus()
            return

        if status == 1 or status == 2:
            
            msgBox = MessageBox()
            msgBox.setText("There is error in your input")
            msgBox.setWindowTitle("Wrong Input")
            msgBox.exec_()
            return
            
            
        if self.old_setting == (self.nsTrt, self.nfTrt, self.nsControl, self.nfControl,
                             self.prioraTrt, self.priorbTrt, self.prioraControl, 
                             self.priorbControl, self.clinSig, self.seed):
            
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
            trial_setting_file.write("Calculation settings:\n")
        
            # Write treatment
            trial_setting_file.write("\nTreatment:\n")
            trial_setting_file.write("\tSuccess\tFailure" + "\n")
            trial_setting_file.write("\t%d\t%d\n"%(self.nsTrt, self.nfTrt))
            trial_setting_file.write("Prior:\t%d\t%d\n"%(self.prioraTrt, self.priorbTrt))
            trial_setting_file.write("\nControl:\n")
            trial_setting_file.write("\tSuccess\tFailure" + "\n")
            trial_setting_file.write("\t%d\t%d\n"%(self.nsControl, self.nfControl))
            trial_setting_file.write("Prior:\t%d\t%d\n"%(self.prioraControl, self.priorbControl))        
            # Clinically significant difference
            trial_setting_file.write("Clinically significant difference:%.3f\n"%(self.clinSig))
            if self.seed_checkBox.isChecked():
            
                trial_setting_file.write("The seed is set: %d\n"%(self.seed))
        
            else:
        
                trial_setting_file.write("A random seed is used: %d\n"%(self.seed))
                
            trial_setting_file.close()
            trial_setting_read = open(configfilename, "r")
            self.parent.mainContent.mainContentWidget.writeConfig(trial_setting_read.read()) 
            self.process = PosteriorProbability_Calculation_Thread(self.nsTrt, self.nfTrt, self.nsControl, self.nfControl,
                                                                   self.prioraTrt, self.priorbTrt, self.prioraControl, 
                                                                   self.priorbControl, self.clinSig, self.seed)
                
            self.process.finishSignal.connect(self.Finish)
            self.process.start()  
                
        except:
            
            exctype,excvalue = sys.exc_info()[:2]
            sys.stdout.write("Error: %s %s" %(str(exctype), str(excvalue)))
            shutil.rmtree(self.fullpathdir)
            self.parent.mainTitle.Finish(0)
        
        self.old_setting = (self.nsTrt, self.nfTrt, self.nsControl, self.nfControl,
                             self.prioraTrt, self.priorbTrt, self.prioraControl, 
                             self.priorbControl, self.clinSig, self.seed)
        
    # Finish
    def Finish(self, flag):
        
        if flag == 0:  
               
            self.finish_flag = 1
            sys.stdout.write("Calculation finished...")
            self.parent.mainTitle.Finish(1)
                        
        else:
                
            self.finish_flag = 0
            sys.stdout.write("Oops, fail to calculate the probability...")
            self.parent.mainTitle.Finish(0)
            shutil.rmtree(self.fullpathdir)
        
    # Reset the whole trial simulator
    def Reset(self):

        self.finish_flag = 0
        self.process = None
        # Reset all the trial settings
        self.nsTrt = self.nfTrt = self.nsControl = self.nfControl = 0
        self.prioraTrt = self.priorbTrt = self.prioraControl = self.priorbControl = 0
        self.clinSig = self.seed = 0
        self.nSuccessTrt_textCtl.clear()
        self.nFailTrt_textCtl.clear()
        self.trtPriorA_textCtl.clear()
        self.trtPriorB_textCtl.clear()
        self.controlPriorA_textCtl.clear()
        self.controlPriorB_textCtl.clear()
        self.nSuccessControl_textCtl.clear()
        self.nFailControl_textCtl.clear()
        self.clinSig_textCtl.clear()
        self.seed_checkBox.setChecked(False)
        self.seed_textCtl.clear()

        
    # Stop
    def Stop(self):
        
        sys.stdout.write("Stop posterior probability calculation")
        self.process.terminate()    
        
        
    def setResult(self):
        
        return 
        
    def setPlot(self):
        
        return
        
        
        
class PosteriorProbability_Calculation_Thread(QtCore.QThread):
    

    finishSignal = QtCore.pyqtSignal(int)    
    def __init__(self, nsTrt, nfTrt, nsControl, nfControl, prioraTrt, priorbTrt, prioraControl, 
                priorbControl, clinSig, seed, parent=None):
        
        super(PosteriorProbability_Calculation_Thread, self).__init__(parent)
        self.nsTrt = nsTrt
        self.nfTrt = nfTrt
        self.nsControl = nsControl
        self.nfControl = nfControl
        self.prioraTrt = prioraTrt
        self.priorbTrt = priorbTrt
        self.prioraControl = prioraControl
        self.priorbControl = priorbControl
        self.clinSig = clinSig
        self.seed = seed
        
        # Create a signal

    # Thread run function
    def run(self):
        
        self.finish_flag = CalPosteriorProbability.CalPosteriorProbability(nTrt = [self.nsTrt, self.nfTrt], 
                                                                           nControl = [self.nsControl, self.nfControl], 
                                                                           priorTrt = [self.prioraTrt, self.priorbTrt], 
                                                                           priorControl = [self.prioraControl, self.priorbControl], 
                                                                           clinSig = self.clinSig, seed = self.seed)
        
        self.finishSignal.emit(self.finish_flag)       
