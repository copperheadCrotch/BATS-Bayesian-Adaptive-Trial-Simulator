# -*- coding: utf-8 -*-
# This is the main GUI for the program
from PyQt5 import QtGui, QtCore, QtWidgets, Qt
import BATS.qrc.resources_qr
# Import Qt GUI
from BATS.ui.maincontentwindow import Ui_MainContentWindow 
# Functions
from BATS.ui.mamswindow import Ui_MAMSWindow
from BATS.ui.posteriorprobabilitywindow import Ui_PosteriorProbabilityWindow
# The look-up table method is banned in the newest version
# from ui.criticalvaluewindow import Ui_CriticalValueTableWindow


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
from BATS.BATS_eventfilter import TableFocusOutFilter
# Import message box
from BATS.BATS_messagebox import MessageBox
from BATS.BATS_messagebox import SubTitleBar
# Import design
from BATS.BATS_MAMS import MAMS_Design
from BATS.BATS_PosteriorProbability import PosteriorProbability_Calculation


# Import module
import sys
import numpy as np
import pandas as pd
import time
import os
import uuid
import shutil
import subprocess
from numpy.random.mtrand import seed
import warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Qt5Agg') 
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import matplotlib.image as mpimg


# Import simulation module
import BATS.FixedTrial as FixedTrial
# import CreateCriticalValueTable as CreateCriticalValueTable
import BATS.PredictiveProbability as PredictiveProbability
import BATS.InterimAnalysis as InterimAnalysis
import BATS.GammaGenerate as GammaGenerate
import BATS.FixedTrialData as FixedTrialData
import BATS.CriticalValueCal as CriticalValueCal
import BATS.AllocFinder as AllocFinder
import BATS.CalPosteriorProbability as CalPosteriorProbability


# Macro/Global variables. Needed only be changed here
# Font color
TITLE_COLOR = QtGui.QColor("#3d5159")
# Normal log color
NORMAL_LOG_COLOR = QtGui.QColor("#3d5159")
# Error log color




# Panel index
SETTING_INDEX = 0
LOG_INDEX = 1
TABLE_INDEX = 2
PLOT_INDEX = 3
                                
# Table Font
TABLE_CELL_FONT = QtGui.QFont('Segoe UI', 10)



# For QString
try:

    _fromUtf8 = QtCore.QString.fromUtf8

except AttributeError:

    def _fromUtf8(s):

        return s


# Setting for the translation of teh text
try:

    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):

        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)

except AttributeError:

    def _translate(context, text, disambig):

        return QtWidgets.QApplication.translate(context, text, disambig)



# Main Window
# Application window, combining two widgets, one sidebar, one main layout
class BATSWindow(QtWidgets.QFrame):


    def __init__(self, parent=None):

        QtWidgets.QFrame.__init__(self, parent)
        # No title bar, but keep the frame
        # self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        # Set position of the frame
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        # Set geometry
        self.setGeometry(self.screen.width()/8, 50, 1600, 900)
        self.setMinimumSize(0, 0)
        # Set Widgets
        self.sideWindow = SideFrame(self)
        self.mainWindow = MainFrame(self)
        # Set Layout
        self.appLayout = QtWidgets.QHBoxLayout()
        self.appLayout.addWidget(self.sideWindow, 2)
        self.appLayout.addWidget(self.mainWindow, 8)
        # Add layout
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.appLayout.setSpacing(0)
        self.setLayout(self.appLayout)
        self.setWindowTitle("Bayesian Adaptive Trial Simulator")


    # Close the application
    def closeEvent(self, event):
        
        # Create a messagebox
        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure you want to exit?")
        msgBox.setWindowTitle("Quit the Simulator")
        result = msgBox.exec_()
        event.ignore()
        if result:

            # Delete all the temporary files
            try:
                
                # Remove the temporary folder if it exists
                shutil.rmtree("./tmp")

            except:
                
                pass
            
            # The objects will be deleted when event started
            self.deleteLater() 
            # Accept the event
            event.accept()
        
            

# Sidebar widget
class SideFrame(QtWidgets.QFrame):


    def __init__(self, parent=None):

        QtWidgets.QFrame.__init__(self, parent)
        # Set layout
        self.sideLayout = QtWidgets.QVBoxLayout()
        # Widgets
        self.sideTitle = SideTitle(parent)
        self.sideSpacer = QtWidgets.QSpacerItem(240, 150)
        self.sideMenu = SideMenu(parent)
        # Run side information
        # Show when running a task
        self.sideRunMenu = SideRunMenu(parent)
        # Hide when intialize
        self.sideRunMenu.setVisible(False)
        # Option
        self.sideOption = SideOption(parent)
        # Add widgets
        self.sideLayout.addWidget(self.sideTitle, 1)
        self.sideLayout.insertStretch(1, 1)
        self.sideLayout.addWidget(self.sideMenu, 7)
        self.sideLayout.addWidget(self.sideRunMenu, 7)
        self.sideLayout.addWidget(self.sideOption, 0)
        # Add layout
        self.sideLayout.setContentsMargins(0, 0, 0, 0)
        self.sideLayout.setSpacing(0)
        self.setLayout(self.sideLayout)
        # Stylesheet
        self.setStyleSheet("background:#399ee5; ")



# Side Title
class SideTitle(QtWidgets.QWidget):

    
    def __init__(self, parent=None):
       
        QtWidgets.QWidget.__init__(self, parent)
        # Add new font
        self.titleFont = QtGui.QFont('Caviar Dreams', 20)
        self.titleFont.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 2.0)
        # Parent widget, application window
        self.parent = parent
        # Mouse
        self.clickPos = QtCore.QPoint(50, 50)
        # Layout
        self.titleLayout = QtWidgets.QHBoxLayout()
        # Icon
        self.iconLabel = QtWidgets.QLabel()
        self.iconLabel.setPixmap(QtGui.QPixmap(":/resources/bcts.png").scaled(QtCore.QSize(100, 100)))
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
        # Title text     
        self.titleLabel = QtWidgets.QLabel("BATS")
        self.titleLabel.setFont(self.titleFont)
        # Stylesheet
        self.setStyleSheet("QLabel{color:#ffffff;}")
        # Add widget
        self.titleLayout.addWidget(self.iconLabel)
        self.titleLayout.addWidget(self.titleLabel)
        # Set layout
        self.titleLayout.setContentsMargins(20, 10, 20, 0)
        self.titleLayout.setSpacing(30)
        self.titleLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.titleLayout)



# Side Menu
class SideMenu(QtWidgets.QListWidget):

    
    def __init__(self, parent=None):
        
        QtWidgets.QListWidget.__init__(self, parent)
        # Get parent
        self.parent = parent
        # List font
        self.listFont = QtGui.QFont("Caviar Dreams")
        self.listFont.setPointSize(14)
        self.listFont.setBold(False)
        self.listFont.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1.0)
        # Customize the widgets
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFont(self.listFont)
        self.horizontalScrollBar().setVisible(False)
        self.setIconSize(QtCore.QSize(50, 50))
        self.setFlow(QtWidgets.QListView.TopToBottom)
        # Design icon
        self.designIcon = QtGui.QIcon()
        self.designIcon.addPixmap(QtGui.QPixmap(":/resources/design.png"), QtGui.QIcon.Normal)
        self.designIcon.addPixmap(QtGui.QPixmap(":/resources/design_selected.png"), QtGui.QIcon.Selected)
        """
        # Table　icon
        self.tableIcon = QtGui.QIcon()
        self.tableIcon.addPixmap(QtGui.QPixmap(":/resources/table.png"), QtGui.QIcon.Normal)
        self.tableIcon.addPixmap(QtGui.QPixmap(":/resources/table_selected.png"), QtGui.QIcon.Selected)
        """
        # Other icon
        self.otherIcon = QtGui.QIcon()
        self.otherIcon.addPixmap(QtGui.QPixmap(":/resources/other.png"), QtGui.QIcon.Normal)
        self.otherIcon.addPixmap(QtGui.QPixmap(":/resources/other_selected.png"), QtGui.QIcon.Selected)
        # Add design items
        self.designItem = QtWidgets.QListWidgetItem(self.designIcon, "Design")
        # self.tableItem = QtWidgets.QListWidgetItem(self.tableIcon, "Table")
        self.otherItem = QtWidgets.QListWidgetItem(self.otherIcon, "Analyze")
        # Add items to the list widget
        self.addItem(self.designItem)
        # self.addItem(self.tableItem)
        self.addItem(self.otherItem)
        # Stylesheet
        self.setStyleSheet("QListWidget{min-width: 100px; border:none; border-top:2px solid #4da8e8; color:#ffffff; margin: 0 0 0 0; padding: 0 0 0 0; text-align:center;} QListWidget::item{border-bottom: 2px solid #4da8e8; padding:15px 25px 15px 25px; margin: 0 0 0 0; text-align: center; background:#399ee5; color:#ffffff;} QListWidget::item:hover{border:none; background:#45c8dc; font-weight:bold;} QListWidget::item:selected{border:none; border-left: 6px solid #fa7064; background:#ffffff; color:#fa7064; font-weight:bold;} QListWidget::icon{margin: 0 0 0 0; padding: 0 20px 0 0;} QLabel{background:transparent; border: none; font-size: 15pt; color:#ffffff; font-family:'Segoe UI';}")
        # Action
        # Select the tab, change the layout
        self.currentRowChanged.connect(self.changeLayout)
        
    
    # Change color
    def changeLayout(self, index):
        
        # Index of the widget
        # 0 is the empty widget
        # 1 is the design widget
        # 2 is the table widget
        # Show the hidden task
        self.parent.mainWindow.mainContent.showTask()
        # Decide the current widget of the main application window
        self.mainWidget = self.parent.mainWindow.mainContent.taskWidget
        # Title
        self.mainTitle = self.parent.mainWindow.mainTitle
        # Panel
        self.mainPanel = self.parent.mainWindow.mainContent.contentPanel
        # Set to the menu option
        self.mainWidget.setCurrentIndex(index)
        # Get Current Task
        self.mainTask = self.mainWidget.currentWidget().currentWidget()
        # Set children widget to 0
        self.mainWidget.currentWidget().setCurrentIndex(0)
        # Set to index of setting
        self.mainPanel.setCurrentRow(0)
        # Set main title
        # Show the buttons
        # Set the title
        self.mainTitle.setVisible(True)
        self.mainTitle.showButton()
        self.mainTitle.taskLabel.setText(self.mainTask.title)
        self.mainTitle.showStatus(0)
        # Setting, log, table, plot
        self.panel_start = self.mainPanel.count()
        if self.mainTask.finish_flag == 1:
            
            self.childrenPanelStart = self.mainTask.panel_start
            self.childrenPanelFinish = self.mainTask.panel_finish
            
            for i in range(0, self.panel_start):
            
                if i in self.childrenPanelStart and i not in self.childrenPanelFinish:
                 
                    self.mainPanel.item(i).setHidden(True)
            
                else:
                
                    self.mainPanel.item(i).setHidden(False)
            
        else:
            
            self.childrenPanelStart = self.mainTask.panel_start
        
            for i in range(0, self.panel_start):
            
                if i in self.childrenPanelStart:
                 
                    self.mainPanel.item(i).setHidden(True)
            
                else:
                
                    self.mainPanel.item(i).setHidden(False)



# Menu shown when running
class SideRunMenu(QtWidgets.QWidget):


    def __init__(self, parent=None):
    
        QtWidgets.QWidget.__init__(self, parent)
        # Layout
        self.runmenulayout = QtWidgets.QVBoxLayout()
        # Widget
        self.runmenuLabel = QtWidgets.QLabel()
        self.runmenuLabel.setText("Task is running\nPlease wait...")
        # self.runmenuMovieLabel = QtWidgets.QLabel()
        # self.runmenuMovie = QtGui.QMovie(":/resources/runmenu.gif")
        # self.runmenuMovieLabel.setMovie(self.runmenuMovie)
        # self.runmenuMovieLabel.show()
        # Add Widget
        self.runmenulayout.addWidget(self.runmenuLabel)
        # self.runmenulayout.addWidget(self.runmenuMovieLabel)
        # Set layout
        self.runmenulayout.setAlignment(QtCore.Qt.AlignCenter)
        self.runmenulayout.setSpacing(0)
        self.runmenulayout.setContentsMargins(10, 0, 10, 0)        
        self.setLayout(self.runmenulayout)
        
        # Stylesheet
        self.setStyleSheet("QLabel{background:transparent; color:#3d5159; font-family:'Segoe UI'; font-size:13pt; border:none;}")
    
    """
    def startMovie(self):
        
        self.runmenuMovie.start()
        
    def stopMovie(self):
        
        self.runmenuMovie.stop()
    """
     
     
        
# Side Option
class SideOption(QtWidgets.QWidget):
 
    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Customize widget
        self.setObjectName("Option")
        # Layout 
        optionLayout = QtWidgets.QHBoxLayout()
        # Option font
        optionFont = QtGui.QFont("Caviar Dreams")
        optionFont.setPointSize(12)
        optionFont.setBold(False)
        optionFont.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1.0)
        # Set widgets
        # Separator
        optionSep = QtWidgets.QWidget()
        optionSep.setStyleSheet("QWidget{background:#4da8e8;}")
        optionSep.setFixedWidth(2)
        # Doc button
        docButton = QtWidgets.QPushButton()
        docButton.setIcon(QtGui.QIcon(":/resources/doc.png"))
        docButton.setIconSize(QtCore.QSize(40, 40))
        docButton.setText("Documentation")
        docButton.setFont(optionFont)
        docButton.setCursor(QtCore.Qt.PointingHandCursor)
        # Layout
        optionLayout.addWidget(docButton, 10)
        # self.optionLayout.setAlignment(QtCore.Qt.AlignCenter)
        optionLayout.setContentsMargins(0, 0, 0, 0)
        optionLayout.setSpacing(0)
        optionLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(optionLayout)
        # Stylesheet
        self.setStyleSheet("QWidget {margin: 0 0 0 0; padding: 0 0 0 0;} QPushButton{background:transparent; border:none; border-top: 2px solid #4da8e8; padding: 0 10px 0 10px; color: #ffffff; outline: none;} QPushButton:hover{background:#45c8dc;}")
        
        # Actiond
        docButton.clicked.connect(self.openDoc)

    def openDoc(self):

        if sys.platform == "win32":

             winfullpathdir = os.getcwd().replace("/", "\\")  + "\\documentation\\Documentation.pdf"
             subprocess.Popen(['explorer', winfullpathdir])

        elif sys.platform == "linux":

            winfullpathdir = os.getcwd() + "/documentation/Documentation.pdf"
            subprocess.Popen(['xdg-open', winfullpathdir])

        elif sys.platform == "darwin":

            winfullpathdir = os.getcwd() + "/documentation/Documentation.pdf"
            subprocess.Popen(['open', winfullpathdir])
     
        else:

            pass
             

# Mainwindow widget
class MainFrame(QtWidgets.QFrame):


    def __init__(self, parent=None):

        QtWidgets.QFrame.__init__(self, parent)
        # Layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        # Widget
        self.mainTitle = MainTitle(parent)
        self.mainSeparator = QtWidgets.QWidget()
        self.mainSeparator.setStyleSheet("background:#e9f0f5; margin: 10px 0 10px 0;")
        self.mainSeparator.setFixedHeight(2)
        self.mainContent = MainContent(self)
        # Add widget
        self.mainLayout.addWidget(self.mainTitle, 0)
        self.mainLayout.addWidget(self.mainSeparator, 1)
        self.mainLayout.addWidget(self.mainContent, 9)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        # Set layout
        self.setLayout(self.mainLayout)
        # Stylesheet
        self.setStyleSheet("background:#ffffff; border: none;")
        
        

# Main Title
class MainTitle(QtWidgets.QWidget):

    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Parent
        self.parent = parent
        # Reciever 
        self.receiver = None
        # Sendin
        self.sendin = None
        # Create a list of error inputs
        self.errorWidgets_list = []
        self.pendingWidgets_list = []
        # Status
        self.status = 0
        # Click pos
        self.clickPos = QtCore.QPoint(50, 50)
        # Title font
        self.taskFont = QtGui.QFont('Segoe UI', 13)
        self.statusFont = QtGui.QFont('PT Sans', 10)
        # Button font
        self.buttonFont = QtGui.QFont("Segoe UI")
        self.buttonFont.setPointSize(11)
        self.buttonFont.setBold(False)
        # Layout
        self.titleLayout = QtWidgets.QHBoxLayout()
        # Widgets
        # Title of the task
        self.taskLabel = QtWidgets.QLabel("")
        self.taskLabel.setStyleSheet("QLabel{padding: 0 25px 0 50px;}")
        self.taskLabel.setGeometry(0, 0, 200, 50)
        self.taskLabel.setFont(self.taskFont)
        # Status button
        # Set status images
        self.statusButton = QtWidgets.QPushButton()
        self.inputIcon = QtGui.QIcon(":/resources/input.png")
        self.errorIcon = QtGui.QIcon(":/resources/error.png")
        self.warningIcon = QtGui.QIcon(":/resources/warning.png")
        self.successIcon = QtGui.QIcon(":/resources/success.png")
        self.statusButton.setIconSize(QtCore.QSize(25, 25))
        self.statusButton.setStyleSheet("QPushButton{background: transparent; border: none; text-align:left; padding: 15px 0 5px 5px; color: #6b767c;} QPushButton:hover{color:#fa7064; border-radius:0;}")
        self.statusButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.statusButton.setGeometry(0, 0, 200, 50)
        self.statusButton.setFont(self.statusFont)
        self.statusButton.setToolTip("Jump to the location")
        self.showStatus(0)

        self.runButton = QtWidgets.QPushButton("Run")
        self.runButton.setFont(self.buttonFont)
        self.runButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.resetButton = QtWidgets.QPushButton("Reset")
        self.resetButton.setFont(self.buttonFont)
        self.resetButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.stopButton = QtWidgets.QPushButton("Stop")
        self.stopButton.setFont(self.buttonFont)
        self.stopButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.stopButton.setStyleSheet("QPushButton{background: #fa7064;border: 1px solid #f43f2f; outline: none;}QPushButton:hover{background: #f84e41;border: 1px solid #f73728;}QPushButton:disabled{background:#acb6ba; border:1px solid #5e7688; color:#fafbfc;}")

        # Add widgets
        self.titleLayout.addWidget(self.taskLabel, 4)
        self.titleLayout.addWidget(self.statusButton, 4)
        self.titleLayout.addWidget(self.runButton, 1)
        self.titleLayout.addWidget(self.resetButton, 1)
        self.titleLayout.addWidget(self.stopButton, 1)
        self.titleLayout.insertStretch(5, 1)

        # Set layout
        self.titleLayout.setSpacing(0)
        self.titleLayout.setContentsMargins(0, 0, 5, 0)
        self.setLayout(self.titleLayout)
        self.setVisible(False)

        # Stylesheet
        self.setStyleSheet("QLabel{color:#6b767c;} QToolButton{border: none; padding: 0 0 0 0;} QToolButton:hover{background:#fa7064;} QPushButton{border:1px solid #2397e8; border-radius:5px; background:#399ee5; color: #ffffff; padding: 5px 15px 5px 15px; margin: 5px 5px 10px 5px; width: 70px; outline:none;} QPushButton:disabled{background:#acb6ba; border:1px solid #5e7688; color:#fafbfc;} QPushButton:hover{background:#66cc6e; border:1px solid #42a54a;}")
        
        # Variable
        # Get the count of the menu
        # self.menucount = parent.sideWindow.sideMenu.count()
        
        # Action
        self.statusButton.clicked.connect(self.jumpStatus)
        self.runButton.clicked.connect(self.Run)
        self.resetButton.clicked.connect(self.Reset)
        self.stopButton.clicked.connect(self.Stop)


    # Show status
    def showStatus(self, status, widget = None):
         
        self.statusButton.setVisible(True)
        # If not finish the input, set the focus to the next input
        if status == 0:
            
            try:
                
                self.sendin = widget
            
            except:
                
                pass
            
            self.statusButton.setIcon(self.inputIcon)
            self.statusButton.setText("Go to the next input")
            
        # If status = 1, on progress, show the next step to do
        elif status == 1:
            
            # Get the current widget
            self.sendin = widget
            self.statusButton.setIcon(self.warningIcon)
            self.statusButton.setText("The input is maybe incomplete")
            
        elif status == 2:
            
            self.sendin = widget
            self.statusButton.setIcon(self.errorIcon)
            self.statusButton.setText("There is invalid input")
            
        elif status == 3:
            
            self.statusButton.setIcon(self.successIcon)            
            self.statusButton.setText("All inputs are valid")
        
        elif status == 4:
            
            self.statusButton.setVisible(False)
                   
        else:
            
            self.showStatus(0)
        
        # Put the current status
        self.status = status
    
    
    # Jump to the current status
    def jumpStatus(self):
        
        self.currentWidget = self.parentWidget().mainContent
        self.currentTask = self.currentWidget.taskWidget.currentWidget().currentWidget()
        # When clicked, set focused
        if self.status == 0:
            
            self.sendin = self.currentTask.quickCheckInput()
            self.sendin.setFocus()
            
        if self.status == 3:
            
            self.runButton.setFocus()
            
        elif self.status == 2:
            
            self.sendin.setFocus()
            
        else:
            
            try:
            
                self.sendin.setFocus()
        
            except:
            
                pass
    
    
    # Show button
    def showButton(self):
        
        self.runButton.setVisible(True)
        self.runButton.setEnabled(True)
        self.resetButton.setVisible(True)
        self.resetButton.setEnabled(True)
        self.stopButton.setVisible(False)
        self.stopButton.setEnabled(True)
        
    
    # Run
    def Run(self):
        
        # Get the current widget
        self.currentWidget = self.parentWidget().mainContent
        # Get the main content widget
        self.currentContent = self.currentWidget.mainContentWidget
        # Get the current panel of the task
        self.currentPanel = self.currentWidget.contentPanel
        # Get the current task running
        self.currentTask = self.currentWidget.taskWidget.currentWidget().currentWidget()
        # Check if all the settings are correct
        run_signal = self.currentTask.checkRun(self.status)
        # Check unsaved results
        # If old settings was run again, escape the check for results, since the results will be the same
        if run_signal == 2:
        
            run_signal = 1
            
        elif run_signal == 1:
               
            run_signal = self.currentContent.checkExportFlow()
          
        # Index for setting
        if run_signal == 1:
            
            # Once run, clean all the widget
            self.currentContent.clearWidget()
            # self.currentTask.printRun()
            self.childrenPanelStart = self.currentTask.panel_start
            for i in self.childrenPanelStart:
                
                self.currentPanel.item(i).setHidden(True)
                
            # self.currentIndex = self.parentWidget().parentWidget().sideBar.sideMenu.currentRow()
            # Disable the setting widget
            self.currentContent.mainStackWidget.widget(0).setEnabled(False)
            # Change the widget to the log and to the bottom
            self.currentPanel.setCurrentRow(1)
            self.currentContent.log_tabWidget.setCurrentIndex(0)
            # Disable left panel
            self.parent.sideWindow.sideMenu.setVisible(False)    
            self.parent.sideWindow.sideRunMenu.setVisible(True)
            # Call the widget's run functions
            self.showStatus(4)
            self.runButton.setEnabled(False)
            self.resetButton.setVisible(False)
            self.stopButton.setVisible(True)   
            # If everything is OK, run the current task
            self.currentTask.Run()        
    
    
    # Reset function
    def Reset(self):
            
        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure you want to reset all the settings?")
        msgBox.setWindowTitle("Reset the settings")
        result = msgBox.exec_()
        # If OK, reset the settings
        if result:
        
            self.currentTask = self.parentWidget().mainContent.taskWidget.currentWidget().currentWidget()
            self.showStatus(0)
            self.currentTask.Reset()
            sys.stdout.write("Reset all the settings")

    
    # Stop
    def Stop(self):

        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure you want to stop the current task?")
        msgBox.setWindowTitle("Stop the task")
        result = msgBox.exec_()
        # If OK, stop the running
        if result: 
            
            self.currentContent.setLogColor("#d8000c")
            sys.stdout.write("Stopping the task...")
            self.currentTask.Stop()
            self.Finish(0)
            sys.stdout.write("Task is stopped")    
            self.currentContent.setLogNormalColor()

          
    # Finish
    def Finish(self, finish_signal):
        
        # Enable setting
        self.currentContent.mainStackWidget.widget(0).setEnabled(True)
        """
        # Change the log viewer to config viewer
        self.currentContent.log_tabWidget.setCurrentIndex(1)
        """
        # 1 success
        # 0 fail
        if finish_signal == 1:
            
            # Show the rest of widgets
            self.childrenPanelFinish = self.currentTask.panel_finish
            for i in self.childrenPanelFinish:
                
                self.currentPanel.item(i).setHidden(False)
            
            # If the index for the table is in, turn to it 
            if TABLE_INDEX in self.childrenPanelFinish:      
          
                self.currentPanel.setCurrentRow(TABLE_INDEX)
                
            # If the index for plot
            elif PLOT_INDEX in self.childrenPanelFinish:
                
                self.currentPanel.setCurrentRow(PLOT_INDEX)
                   
            # Check if the there is result and plot view function
            self.callableresult = getattr(self.currentTask, "setResult", None)
            if callable(self.callableresult):
            
                self.currentTask.setResult()
        
            # If plot function exist, run
            self.callableplot = getattr(self.currentTask, "setPlot", None)
            if callable(self.callableplot):
            
                self.currentTask.setPlot()
        
        else:
            
            self.currentPanel.setCurrentRow(SETTING_INDEX)
        
        # Enable widgets
        self.parent.sideWindow.sideMenu.setVisible(True)
        self.parent.sideWindow.sideRunMenu.setVisible(False)
        # Enable buttons
        self.runButton.setEnabled(True)
        self.resetButton.setVisible(True)
        self.stopButton.setVisible(False)
             
        
# Main Content
class MainContent(QtWidgets.QWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Layout
        self.mainLayout = QtWidgets.QHBoxLayout()
        # Widgets
        self.mainContentWidget = MainContentWindow(self)
        self.taskWidget = QtWidgets.QStackedWidget()
        self.taskMannualWidget = QtWidgets.QDockWidget("Manual")
        # self.taskMannualWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.taskMannualWidget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.taskMannualWidget.setAllowedAreas(QtCore.Qt.RightDockWidgetArea|QtCore.Qt.LeftDockWidgetArea)
        self.taskMannualWidget.setStyleSheet("QDockWidget{border: 2px solid #00529b; margin: 0; font-size: 12pt; color:#399ee5; font-family: 'PT Sans' ;} QDockWidget::title{padding-left: 10px; background: #d8dde6;}")
        self.taskMannual = QtWidgets.QTextBrowser()
        self.taskMannual.setFocusPolicy(QtCore.Qt.NoFocus)
        self.taskMannual.setStyleSheet("QTextBrowser{margin: 0; border: 2px solid #d8dde6; border-top:none; border-radius:0;}")
        self.taskMannualWidget.setWidget(self.taskMannual)
        self.taskMannualWidget.setMinimumWidth(350)
        
        
        # Set icon
        self.taskShowToggleOn = QtGui.QIcon(":/resources/toggle_on.png")
        self.taskShowToggleOff = QtGui.QIcon(":/resources/toggle_off.png")        
        # Set button
        self.taskShowButton = QtWidgets.QPushButton()
        self.taskShowButton.setIconSize(QtCore.QSize(20, 20))
        self.taskShowButton.setIcon(self.taskShowToggleOff)
        self.taskShowButton.setMaximumWidth(25)
        self.taskShowButton.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        self.taskShowButton.setCursor(QtCore.Qt.PointingHandCursor)
        self.taskShowButton.setToolTip("Open Manual")
        self.taskShowButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.taskShowButton.setStyleSheet("QPushButton{border-radius: 0; margin: 0; background:#d8dde6; border:none;} QPushButton:hover{background:#d8dde6;}")
        # self.mainContentWidget.mainSettingLayout.addWidget(self.taskMannualWidget)
        # Add window widget
        self.subTaskWindow = MainContentSetting()
        self.subTaskWidget = QtWidgets.QWidget()
        self.subTaskLayout = QtWidgets.QHBoxLayout()
        self.subTaskLayout.setContentsMargins(0, 0, 0, 0)
        self.subTaskLayout.setSpacing(0)
        self.subTaskLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.subTaskLayout.addWidget(self.taskWidget)
        self.subTaskLayout.addWidget(self.taskShowButton)
        self.subTaskWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.taskMannualWidget)
        self.subTaskWidget.setLayout(self.subTaskLayout)
        self.subTaskWindow.setCentralWidget(self.subTaskWidget)
        
        self.mainContentWidget.mainSettingLayout.addWidget(self.subTaskWindow)
        # Nested widget
        # Design
        self.designcontentWidget = DesignContent(parent)
        self.designcontentWidget.setCurrentIndex(0)
        """
        # Table
        self.tablecontentWidget = TableContent(parent)
        self.tablecontentWidget.setCurrentIndex(0)
        """
        # Other functions
        self.othercontentWidget = OtherContent(parent)
        self.othercontentWidget.setCurrentIndex(0)
        # Control panel
        self.contentPanel = MainContentPanel(self)
        self.contentPanel.setCurrentRow(-1)
        # Add widgets
        # Add an empty widget as initial
        self.taskWidget.addWidget(self.designcontentWidget)
        # self.taskWidget.addWidget(self.tablecontentWidget)
        self.taskWidget.addWidget(self.othercontentWidget)
        # Area
        # Add widget
        self.mainLayout.addWidget(self.mainContentWidget, 9)
        self.mainLayout.addWidget(self.contentPanel, 1)
        # SetLayout
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)
        
        # Style of the widget
        self.mainContentWidget.setVisible(False)
        # Stylesheet
        self.setStyleSheet("border: none; font-family:'Segoe UI';")
        
        # Action
        self.taskShowButton.clicked.connect(self.showMannual)
        
    
    def clearDoc(self):
        
        self.taskMannual.clear()
    
    def showTask(self):
        
        self.mainContentWidget.setVisible(True) 
        
    # Set documentation
    def setDoc(self, url):
        
        try:
        
            self.taskMannual.setSource(QtCore.QUrl(url))
        
        except:
            
            pass
            
        
    """       
    def resizeDock(self, flag):
        
        # The dockwidget is floating now
        if flag == True:
            
            screen = QtWidgets.QDesktopWidget().screenGeometry()
            self.taskMannualWidget.setGeometry(screen.width()/8, 50, 800, 600)
    """
        
        
    def showMannual(self):
        
        if self.taskMannualWidget.isVisible() == True:
            
            self.taskMannualWidget.setVisible(False)
            self.taskShowButton.setIcon(self.taskShowToggleOn)
        
        else:
            
            self.taskMannualWidget.setVisible(True)
            self.taskShowButton.setIcon(self.taskShowToggleOff)        
        

# Main Content Panel
class MainContentPanel(QtWidgets.QListWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QListWidget.__init__(self, parent)
        self.parent = parent
        self.setFocusPolicy(False)
        self.horizontalScrollBar().setVisible(False)
        # Customize the list widget
        self.setIconSize(QtCore.QSize(60, 60))
        # Icon only
        self.settingItem = QtWidgets.QListWidgetItem(QtGui.QIcon(":/resources/result_setting.png"), "")
        self.settingItem.setToolTip("Setting")
        self.logItem = QtWidgets.QListWidgetItem(QtGui.QIcon(":/resources/result_log.png"), "")
        self.logItem.setToolTip("Log")
        self.tableItem = QtWidgets.QListWidgetItem(QtGui.QIcon(":/resources/result_table.png"), "")
        self.tableItem.setToolTip("Results")
        self.plotItem = QtWidgets.QListWidgetItem(QtGui.QIcon(":/resources/result_plot.png"), "")
        self.plotItem.setToolTip("Plots")
        self.addItem(self.settingItem)
        self.addItem(self.logItem)
        self.addItem(self.tableItem)
        self.addItem(self.plotItem)
        
        # Hide icon
        self.settingItem.setHidden(True)
        self.logItem.setHidden(True)
        self.tableItem.setHidden(True)
        self.plotItem.setHidden(True)
    
        # Stylesheet
        self.setStyleSheet("QListWidget{min-width:90px; background:#f7fafc;border:none;border-left: 2px solid #e9f0f5;}QListWidget::item{background: #f7fafc;background-origin: cotent;background-clip: margin;color: #000000;margin: 0 0 0 10px;padding: 25px 0 25px 0px;}QListWidget::item:selected{background: #bac3ef;position: fixed;}QLabel{background: transparent;border: none;}")
        
        # Signal
        self.currentRowChanged.connect(self.viewChange)
                
                
    # Swith function
    def viewChange(self, index):
        
        # Change corresponding index
        self.parent.mainContentWidget.mainStackWidget.setCurrentIndex(index)



# Main sub content
class MainContentWindow(QtWidgets.QWidget, Ui_MainContentWindow):
 
    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        # Store plot
        self.parent = parent
        self.table_file = None
        self.plot_file = {}
        self.exportTable_flag = self.exportPlot_flag = 0
        # Set font size amd color for log console
        self.log_tabWidget.setCurrentIndex(0)
        self.log_tabWidget.setTabIcon(0, QtGui.QIcon(":/resources/tab_log.png"))
        self.log_tabWidget.setTabIcon(1, QtGui.QIcon(":/resources/tab_info_disabled.png"))
        self.log_tabWidget.tabBar().setTabTextColor(0, QtGui.QColor("#4f8a10"))  
        self.log_tabWidget.tabBar().setStyleSheet("QTabBar:tab:selected{ border-color: #4f8a10;}")
        font = QtGui.QFont("Segoe UI", 10)
        self.logConsole.setFont(font)
        self.configConsole.setFont(font)
        self.configConsole.setTextColor(QtGui.QColor("#00529B"))
        self.verticalHeaderFont = font
        self.logConsole.setTextColor(NORMAL_LOG_COLOR)
        # Link the stdout to log textedit
        self.originalsys = sys.stdout
        sys.stdout = StdOutStream()
        # self.wheelfilter = WheelFilter()
        # self.graph_comboBox.installEventFilter(self.wheelfilter)
        # Set current index to the comboBox
        # self.graph_comboBox.setCurrentIndex(-1)

        
        # Action
        self.log_tabWidget.currentChanged.connect(self.changeTab)
        sys.stdout.textWritten.connect(self.writeLog)
        self.logClear_btn.clicked.connect(self.clearLog)
        # self.graph_comboBox.currentIndexChanged.connect(self.changeGraph)
        self.tableExport_btn.clicked.connect(self.exportTable)
        self.plotExport_btn.clicked.connect(self.exportPlot)
    
    
    # Function for the log tab
    def changeTab(self, index):
        
        if index == 0:
            
            self.log_tabWidget.setTabIcon(0, QtGui.QIcon(":/resources/tab_log.png"))
            self.log_tabWidget.setTabIcon(1, QtGui.QIcon(":/resources/tab_info_disabled.png"))
            self.log_tabWidget.tabBar().setTabTextColor(0, QtGui.QColor("#4f8a10"))     
            self.log_tabWidget.tabBar().setStyleSheet("QTabBar:tab:selected{ border-color: #4f8a10;} QTabBar:tab:selected:hover{color:#4f8a10;}") 
                  
        else:
            
            self.log_tabWidget.setTabIcon(0, QtGui.QIcon(":/resources/tab_log_disabled.png"))
            self.log_tabWidget.setTabIcon(1, QtGui.QIcon(":/resources/tab_info.png"))
            self.log_tabWidget.tabBar().setTabTextColor(1, QtGui.QColor("#00529b"))
            self.log_tabWidget.tabBar().setStyleSheet("QTabBar:tab:selected{ border-color: #00529b;} QTabBar:tab:selected:hover{color:#00529b;}")
        

    # Write log
    def writeLog(self, text):
          
        self.logConsole.verticalScrollBar().setValue(self.logConsole.verticalScrollBar().maximum())        
        if "Error" in text or "Oops" in text:
            
            self.logConsole.setTextColor(QtGui.QColor("#d8000c"))
            self.logConsole.append(text)
            self.logConsole.setTextColor(NORMAL_LOG_COLOR)
            
        else: 
           
            self.logConsole.append(text)
          
    
    def writeConfig(self, text):

        self.configConsole.verticalScrollBar().setValue(self.configConsole.verticalScrollBar().maximum())        
        self.configConsole.append(text)
        
    
    # Set log color
    def setLogColor(self, color):
        
        self.logConsole.setTextColor(QtGui.QColor(color))        


    # Set log normal color
    def setLogNormalColor(self):
        
        self.logConsole.setTextColor(NORMAL_LOG_COLOR)


    # Clear log
    def clearLog(self):

        if self.log_tabWidget.currentIndex() == 0:
            
            self.logConsole.verticalScrollBar().setValue(0)        
            self.logConsole.clear()
        
        else:
            
            self.configConsole.verticalScrollBar().setValue(0)
            self.configConsole.clear()

    
    # Call back the result
    def setCallbackResult(self, finalfile, header_index):
        
        self.tableArea.verticalScrollBar().setValue(0)
        # Result layout
        result_layout = QtWidgets.QVBoxLayout()
        # Set layout
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(30)
        # Read the data file
        df = pd.read_csv(finalfile)
        # Index 0 is the main
        index_count = len(header_index)
        # Index name
        index_name = {}
        # Index name list
        index_name_list = []
        # Get the column names
        column_names = df.columns.values
        # Get number of columns
        column_count = df.shape[1]
        # Create a range, not include the index
        column_valid = range(index_count, column_count)
        # If two index:
        if index_count == 1:
            
            pass
        
        elif index_count == 2:
            
            for i in header_index:
            
                index_name_list = []
                for j in df.ix[:, i]:
                    
                    if j in index_name_list:
                        
                        continue
                    
                    else:
                        
                        index_name_list.append(j)
                        
                index_name[i] = index_name_list
               
            n_index0 = len(index_name[0])
            n_index1 = len(index_name[1]) 
                
            # Use pivot to create table
            for j in column_valid:
                
                name = column_names[j]
                single_result = QtWidgets.QFrame()
                single_result.setMinimumHeight((n_index0 + 1) * 120  + 100)
                single_result.setStyleSheet("QFrame{background:#f9fafc;font-family:'Segoe UI';border: 1px solid #f9fafc;border-radius: 5px;max-height: 1600px;}")
                # Layout
                single_result_layout = QtWidgets.QVBoxLayout()
                # Title
                single_main_title = QtWidgets.QLabel()
                single_main_title.setText(name)
                single_main_title.setStyleSheet("QLabel{color:#7e888c; font-family:'Segoe UI'; font-size:11pt;}")
                # Text Browser
                single_main_browser = QtWidgets.QTextBrowser()
                url = "qrc:///doc/result/" + name + ".html"
                single_main_browser.setSource(QtCore.QUrl(url))
                single_main_browser.setStyleSheet("QTextBrowser{background:transparent;max-height:100px; margin-top: 10px; margin-bottom:20px;}")
                # Table
                single_main_table = QtWidgets.QTableWidget()
                # Table style
                # Dataframe pivot
                new_df = df.pivot(index = column_names[0], columns = column_names[1], values = column_names[j])
                single_main_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                single_main_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                single_main_table.horizontalHeader().setMinimumHeight(60)
                single_main_table.horizontalHeader().setMinimumSectionSize(60) 
                single_main_table.horizontalHeader().setMaximumSectionSize(120) 
                single_main_table.verticalHeader().setMinimumSectionSize(80) 
                single_main_table.verticalHeader().setMaximumSectionSize(120) 
                single_main_table.verticalHeader().setFont(self.verticalHeaderFont)
                single_main_table.horizontalHeader().setSectionsClickable(False)
                single_main_table.verticalHeader().setSectionsClickable(False)
                single_main_table.horizontalScrollBar().setVisible(False)
                single_main_table.verticalScrollBar().setVisible(False)
                single_main_table.setFocusPolicy(QtCore.Qt.NoFocus)
                single_main_table.setStyleSheet("QTableWidget{border: none; background:transparent; outline:none; gridline-color: #ffffff;} QTableWidget QTableCornerButton::section{background:#f7fafc; border: none;} QHeaderView:Section{background:transparent; border:none; padding: 0 5px 5px 5px;} QTableWidget::item{border:none; color:#66cc6e; font-size: 12pt; font-family:'Segoe UI Light'; text-align:center;} QLineEdit{border: none; }")
                single_main_table.setRowCount(n_index0)
                single_main_table.setColumnCount(n_index1)
                single_main_table.setHorizontalHeaderLabels(index_name[1])
                single_main_table.setVerticalHeaderLabels(index_name[0])
                for k in range(n_index0):
                    
                    for m in range(n_index1):
                        
                        # Align at center
                        if pd.isnull(new_df.ix[k, m]):
                            
                            item = QtWidgets.QTableWidgetItem("-")
                            
                        else:
                            
                            item = QtWidgets.QTableWidgetItem(str(np.around(new_df.ix[k, m], 3)))
                        
                        # Disable edit
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                        item.setTextAlignment(QtCore.Qt.AlignCenter)
                        item.setFont(TABLE_CELL_FONT)
                        single_main_table.setItem(k, m, item)
                
                # single_main_table.resizeRowsToContents()
                # Add widget
                single_result_layout.addWidget(single_main_title)
                single_result_layout.addWidget(single_main_browser, 1)
                single_result_layout.addWidget(single_main_table)
                # Set layout
                single_result_layout.setContentsMargins(15, 30, 15, 30)
                single_result_layout.setSpacing(0)
                single_result.setLayout(single_result_layout)
                # self.tableLayout.addWidget(single_result)        
                result_layout.addWidget(single_result)
        
        # Table layout are made to only output one file this time    
        self.tableLayout.addLayout(result_layout)
        self.table_file = df
        self.exportTable_flag = -1

        
        
    def setCallbackPlot(self, filedir):

        self.plot_file = {}
        # Delete previous widgets
        for root, dir, files in os.walk(filedir):
            
            for file in files:
                
                if file.endswith(".png"):
                
                    filename = file.rsplit(".", 1)[0]
                    root_index = root.rsplit("/", 1)[1]
                    if root_index in self.plot_file:
                    
                        if file != "ui.png":
                        
                            self.plot_file[root_index].append(root + "/" + file)
        
                    else:
                        
                        self.plot_file[root_index] = [root + "/ui.png"]
                        if file != "ui.png":
                        
                            self.plot_file[root_index].append(root + "/" + file)
        
        row_pos = col_pos = 0
        
        for root_index in range(0, len(self.plot_file.keys())):
                
            row_pos = int(root_index/2)
            col_pos = root_index % 2
            root_name = list(self.plot_file.keys())[root_index]
            currentfile = self.plot_file[root_name][0]
            plot_frame = SubGraphViewer(self, root_name, currentfile)
            self.plotViewer.addWidget(plot_frame, row_pos, col_pos, QtCore.Qt.AlignTop)
        
        # self.plotViewer.addItem(QtWidgets.QSpacerItem(20, 60, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), row_pos + 1, 0)
        # self.graph_comboBox.setCurrentIndex(-1)
        self.exportPlot_flag = -1
    
    
    def changeGraph(self, index):
         
        if index == -1:
            
            self.plotViewer.setVisible(False)
        
        else:
            
            self.plotViewer.setVisible(True)
            # self.plotViewer.fitInView(scene.sceneRect())


    # Export table
    def exportTable(self):
        
        self.table_output_file, filetype = QtWidgets.QFileDialog.getSaveFileName(self, "Export Tables To...", "", "CSV(*.csv);;HTML(*.html)")
        if filetype == "CSV(*.csv)":
            
            self.table_file.to_csv(self.table_output_file, index = False)
            sys.stdout.write("Output result files to %s"%(self.table_output_file))
            self.exportTable_flag = 1
            
        elif filetype == "HTML(*.html)":
            
            self.table_file.to_html(self.table_output_file, index = False)
            sys.stdout.write("Output result files to %s"%(self.table_output_file))
            self.exportTable_flag = 1
    
    
    # Export plot
    def exportPlot(self):
        
        # Combine to one 
        self.plot_output_file, filetype = QtWidgets.QFileDialog.getSaveFileName(self, "Export Plots To...", "", "PDF(*.pdf)")
        if filetype == "PDF(*.pdf)":
      
            pdf = matplotlib.backends.backend_pdf.PdfPages(self.plot_output_file)
            for key in self.plot_file.keys():
                
                for i in range(1, len(self.plot_file[key])):
               
                    fig = plt.figure()
                    img = mpimg.imread(self.plot_file[key][i])
                    plt.imshow(img)
                    plt.axis('off')
                    pdf.savefig(fig)
                    plt.clf()
                    plt.close()
                
            pdf.close()
            sys.stdout.write("Output plot files to %s"%(self.plot_output_file))      
            self.exportPlot_flag = 1
        
        
    def checkExportFlow(self):
        
        # if 0, there is no check
        # if -1, there needs to be check
        if self.exportTable_flag == -1 and self.exportPlot_flag == -1:
            
            msgBox = MessageBox(None, 2)
            msgBox.setText("Are you sure to start the new task, there are unsaved results")
            msgBox.setWindowTitle("Unsaved Results")
            result = msgBox.exec_()   
            if result:

                self.exportTable_flag = 1
                self.exportPlot_flag = 1
                return 1

            else:
            
                self.parent.contentPanel.setCurrentRow(TABLE_INDEX)
                return
            
        elif self.exportTable_flag == -1:
            
            return self.checkExportTable()
            
        elif self.exportPlot_flag == -1:
            
            return self.checkExportPlot()
           
        return 1
     

    def checkExportTable(self):
        
        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure to start the new task, there are unsaved results")
        msgBox.setWindowTitle("Unsaved Results")
        result = msgBox.exec_()
        if result:

            self.exportTable_flag = 1
            return 1

        else:
            
            self.parent.contentPanel.setCurrentRow(TABLE_INDEX)
            return
            
        
    def checkExportPlot(self):
        
        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure to start the new task, there are unsaved plots")
        msgBox.setWindowTitle("Unsaved Results")
        result = msgBox.exec_()
        if result:

            self.exportPlot_flag = 1
            return 1
 
        else:
            
            self.parent.contentPanel.setCurrentRow(PLOT_INDEX)
            return
        

    def clearWidget(self):
        
        
        self.clearPlotWidget(self.tableLayout)
        self.clearTableWidget(self.plotViewer)
        
        
    def clearTableWidget(self, layout):
        
        
        layout_exist = layout.count()
        if layout_exist > 0:
            
            for i in reversed(range(layout_exist)):
                
                item = layout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    
                    widget.deleteLater()
                    
                elif item.layout() is not None:
                
                    self.clearTableWidget(item.layout())
        
        
    def clearPlotWidget(self, layout):
        
        
        layout_exist = layout.count()
        if layout_exist > 0:
            
            for i in reversed(range(layout_exist)):
                
                item = layout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    
                    widget.deleteLater()
                    
                elif item.layout() is not None:
                
                    self.clearTableWidget(item.layout())


    # Delete function
    def __del__(self):

        sys.stdout = self.originalsys



# MainContent Setting
class MainContentSetting(QtWidgets.QMainWindow):
    
    def __init__(self, parent = None):
        
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Widget)  
        
        
        

class DesignContent(QtWidgets.QStackedWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QStackedWidget.__init__(self, parent)
        # Design widget
        self.mamsWidget = MAMS_Design(parent)
        self.addWidget(self.mamsWidget)


"""
class TableContent(QtWidgets.QStackedWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QStackedWidget.__init__(self, parent)   
        # Critical value look-up table 
        self.criticalvalueWidget = CriticalValue_Table(parent)
        self.addWidget(self.criticalvalueWidget)    
         
         
"""         
class OtherContent(QtWidgets.QStackedWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QStackedWidget.__init__(self, parent)
        self.posteriorprobWidget = PosteriorProbability_Calculation(parent)
        self.addWidget(self.posteriorprobWidget)
        

# Window for plots
class SubGraphViewer(QtWidgets.QFrame):
            
    def __init__(self, parent = None, root_name = "", currentfile = ""):
        
        QtWidgets.QFrame.__init__(self, parent)
        self.parent = parent
        self.setMinimumHeight(400)
        self.setMaximumHeight(400)
        self.plot_font = QtGui.QFont('Bitter', 11)
        self.setStyleSheet("QFrame{border: 2px solid #e9f0f5; border-radius:5px; border-left:4px solid #baddef;} QFrame:hover{border: 2px solid #faaba4; border-left:4px solid #fa7064; color: #55b1f2; }")
        self.plot_layout = QtWidgets.QVBoxLayout()
        self.plot_title_layout = QtWidgets.QHBoxLayout()
        self.plot_title = QtWidgets.QLabel()
        # Read only the name
        self.plot_title.setText(root_name)
        self.plot_title.setFont(self.plot_font)
        self.plot_title.setStyleSheet("QLabel {border: none;}")
        self.plot_title.setWordWrap(True)
        self.plot_title_layout.insertStretch(0, 2)
        self.plot_title_layout.addWidget(self.plot_title, 6)
        self.plot_title_layout.insertStretch(2, 2)
        self.plot_graph = GraphLabel()
        self.plot_graph.setMargin(0)
        self.plot_graph.setStyleSheet("QLabel{border: none;}")
        self.currentdir = currentfile.rsplit("/", 1)[0]
        self.currentpixmap = QtGui.QPixmap(currentfile).scaled(QtCore.QSize(300, 300))
        self.plot_graph.setPixmap(self.currentpixmap)
        self.plot_graph.setAlignment(QtCore.Qt.AlignCenter)
        self.plot_layout.addWidget(self.plot_graph)
        self.plot_layout.addLayout(self.plot_title_layout)
        self.plot_layout.setContentsMargins(5, 5, 5, 10)
        self.plot_layout.setSpacing(0)
        self.setLayout(self.plot_layout)
        
        self.root_name = root_name
        # Click event
        self.plot_graph.clicked.connect(self.openAllGraph)
        # Display
        # self.show()
        
        
    def openAllGraph(self):
        
        self.plot_file_list = self.parent.plot_file[self.root_name]
        self.graphviewer = QtWidgets.QFrame()
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        # Set geometry
        self.graphviewer.setGeometry(self.screen.width()/4, 100, 800, 600)
        self.graphviewer.setWindowFlags(QtCore.Qt.Popup)
        self.graphviewer.setObjectName("graphView")
        self.graphviewer.setStyleSheet("QFrame#graphView{background:#ffffff;border:0.5px solid #fa7064;} QPushButton:hover{background:#6e66cc;border:1px solid #373366;} QToolButton:hover{background:#fa7064;}")
        # self.graphviewer.setWindowModality(QtCore.Qt.WindowModal)
        # Layout
        graph_layout = QtWidgets.QVBoxLayout()
        # Title
        graph_title = SubTitleBar(self.graphviewer)
        graph_title.title_Label.setText(self.root_name)
        # Separator line
        hline = QtWidgets.QWidget()
        hline.setStyleSheet("QWidget{min-height:2px; max-height:2px; background:#399ee5;}")
        # ComboBox
        graph_control = QtWidgets.QWidget()
        graph_control_layout = QtWidgets.QHBoxLayout()
        self.graph_control_comboBox = QtWidgets.QComboBox()
        self.graph_control_comboBox.setStyleSheet("QComboBox{font-family:'Segoe UI';font-size: 10pt;border: 1px solid #c5d2d9; border-radius:5px;padding: 5px 10px 5px 10px; color: #66767c;min-width: 250px;} QComboBox:hover{border: 2px solid #2a4d69;border-radius: 5px;height: 30ps;} QComboBox::drop-down {subcontrol-origin: padding; subcontrol-position: top right;width: 40px;border-left-width: 2px;border-left-color: #c5d2d9;border-left-style: solid; border-top-right-radius: 5px; border-bottom-right-radius: 5px;padding: 1px 1px 1px 1px;image: url(:/resources/dropdown_arrow.png);} QComboBox QAbstractItemView {border: 1px solid #c5d2d9; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px;selection-background-color:#4b86b4;outline: solid #2a4d69;font-family: 'Segoe UI';font-size: 10pt;color: #66767c;}")
        graph_control_layout.insertStretch(0, 4)
        graph_control_layout.addWidget(self.graph_control_comboBox)
        graph_control_layout.insertStretch(3, 4)
        graph_control.setLayout(graph_control_layout)
        # Main Content
        self.graph_content = QtWidgets.QStackedWidget()
        # Add stack
        for i in range(1, len(self.plot_file_list)):
            
            currentName = self.plot_file_list[i].rsplit("/", 1)[1].rsplit(".", 1)[0]
            self.graph_control_comboBox.addItem(currentName)
            graph_label = QtWidgets.QLabel()            
            currentGraph = QtGui.QPixmap(self.plot_file_list[i])
            graph_label.setPixmap(currentGraph)
            graph_label.setAlignment(QtCore.Qt.AlignCenter)
            self.graph_content.addWidget(graph_label)
        
        # Add layout
        graph_layout.addWidget(graph_title, 1)
        graph_layout.addWidget(hline, 1)     
        graph_layout.addWidget(graph_control, 1)   
        graph_layout.addWidget(self.graph_content, 8)
        graph_layout.setContentsMargins(5, 10, 5, 10)
        graph_layout.setAlignment(QtCore.Qt.AlignTop)
        self.graphviewer.setLayout(graph_layout)
        self.graph_control_comboBox.currentIndexChanged.connect(self.changeGraph)
        self.graphviewer.show()
        
    
    def changeGraph(self, index):
        
        self.graph_content.setCurrentIndex(index)

        

class GraphLabel(QtWidgets.QLabel):
    
    clicked = QtCore.pyqtSignal()
    def __init__(self, parent = None):
         
        QtWidgets.QLabel.__init__(self, parent)
        
    def mouseReleaseEvent(self, event):
        
        self.clicked.emit()


    
# Std write out
class StdOutStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        
        self.textWritten.emit(str(text))
        QtCore.QCoreApplication.processEvents()
    
    def flush(self):
    
        pass



# Splashscreen
class MovieSplashScreen(QtWidgets.QSplashScreen):

    def __init__(self, movie, parent = None):

        movie.jumpToFrame(0)
        pixmap = QtGui.QPixmap(movie.frameRect().size())
        QtWidgets.QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):

        self.movie.start()

    def hideEvent(self, event):

        self.movie.stop()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)

    def sizeHint(self):

        return self.movie.scaledSize()


# The main function if started from Python
def main():
    
    # Set a unique id to BATS
    import ctypes
    appid = u'bats.1.1.0'
    # Check the platform. If windows, set an ID so it will be in the task bar.
    if sys.platform == 'win32':

       ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    
    elif sys.platform == 'linux':

       pass

    elif sys.platform == 'darwin':

        pass
    
    else:
      
      sys.stdout.write("The application is not supported in this system")
      pass
    
    # Create the application
    app = QtWidgets.QApplication(['Bayesian Adaptive Trial Simulator'])
    # Add icon for the application
    app_icon = QtGui.QIcon()
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(16,16))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(24,24))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(32,32))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(48,48))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)
    # Add font to the font database
    QtGui.QFontDatabase().addApplicationFont(":/resources/font/Caviar_Dreams_Bold.ttf")
    QtGui.QFontDatabase().addApplicationFont(":/resources/font/PTsans.ttf")
    # Initialize the GUI
    window = BATSWindow()
    window.show()
    # Run the app
    sys.exit(app.exec_())

    
    
# Initialize of the app
if __name__ == '__main__':
    
    # The main function
    main()
