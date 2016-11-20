# -*- coding: utf-8 -*-
# This is the main GUI for the program
from PyQt5 import QtGui, QtCore, QtWidgets
import qrc.resources_qr
# Import Qt GUI
from ui.maincontentwindow import Ui_MainContentWindow 
# Functions
from ui.mamswindow import Ui_MAMSWindow
from ui.criticalvaluewindow import Ui_CriticalValueTableWindow


# Import module
import sys
import numpy as np
import pandas as pd
import time
import os
import uuid
import shutil
import subprocess
import warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use('Qt5Agg') 
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import matplotlib.image as mpimg


# Import simulation module
import FixedTrial as FixedTrial
import CreateCriticalValueTable as CreateCriticalValueTable
import PredictiveProbability as PredictiveProbability
import InterimAnalysis as InterimAnalysis
import GammaGenerate as GammaGenerate
import FixedTrialData as FixedTrialData
import CriticalValueCal as CriticalValueCal
import Bisection as Bisection
import AllocFinder as AllocFinder



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
class ApplicationWindow(QtWidgets.QFrame):


    def __init__(self, parent=None):

        QtWidgets.QFrame.__init__(self, parent)
        # No title bar, but keep the frame
        # self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        # Set position of the frame
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        # Set geometry
        self.setGeometry(self.screen.width()/5, 50, 1400, 900)
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
        self.setWindowTitle("  ")


    # Close the application
    def closeEvent(self, event):

        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure you want to exit?")
        msgBox.setWindowTitle("Quit the Simulator")
        result = msgBox.exec_()
        event.ignore()
        if result:

            # Delete all the temporary files
            try:
            
                shutil.rmtree("./tmp")

            except:
                
                pass
            
            # Close all the windows
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
        
    """
    # Rewrite mouse press event    
    def mousePressEvent(self, event):
        
        if event.button() == QtCore.Qt.LeftButton:

            self.startPos = event.globalPos()
            self.clickPos = self.mapToParent(self.pos())
    
    
    # Rewrite mouse move event, move the frame    
    def mouseMoveEvent(self, event):
        
        # Move the main application
        self.parent.move(event.globalPos() - self.clickPos)
    """


# Side Menu
class SideMenu(QtWidgets.QListWidget):

    
    def __init__(self, parent=None):
        
        QtWidgets.QListWidget.__init__(self, parent)
        # Get parent
        self.parent = parent
        # List font
        self.listFont = QtGui.QFont('Segoe UI')
        self.listFont.setPointSize(14)
        self.listFont.setBold(False)
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
        # Table　icon
        self.tableIcon = QtGui.QIcon()
        self.tableIcon.addPixmap(QtGui.QPixmap(":/resources/table.png"), QtGui.QIcon.Normal)
        self.tableIcon.addPixmap(QtGui.QPixmap(":/resources/table_selected.png"), QtGui.QIcon.Selected)
        # Other icon
        self.otherIcon = QtGui.QIcon()
        self.otherIcon.addPixmap(QtGui.QPixmap(":/resources/other.png"), QtGui.QIcon.Normal)
        self.otherIcon.addPixmap(QtGui.QPixmap(":/resources/other_selected.png"), QtGui.QIcon.Selected)
        # Add design items
        self.designItem = QtWidgets.QListWidgetItem(self.designIcon, "Design")
        self.tableItem = QtWidgets.QListWidgetItem(self.tableIcon, "Table")
        self.otherItem = QtWidgets.QListWidgetItem(self.otherIcon, "Other")
        # Add items to the list widget
        self.addItem(self.designItem)
        self.addItem(self.tableItem)
        # Enable this in the next version
        # Other function include 'sample size calculation, predictive probability calculation...'
        # self.addItem(self.otherItem)
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
        # Setting, log, table, plot
        self.panel_start = self.mainPanel.count()
        if self.mainTask.finishflag == 1:
            
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
        optionFont = QtGui.QFont("Segoe UI")
        optionFont.setPointSize(12)
        optionFont.setBold(False)
        # Set widgets
        # Quit button
        # quitButton = QtWidgets.QPushButton()
        # quitButton.setIcon(QtGui.QIcon(":/resources/quit.png"))
        # quitButton.setIconSize(QtCore.QSize(50, 50))
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
        # Layout
        # optionLayout.addWidget(quitButton, 2)
        # optionLayout.addWidget(optionSep, 2)
        optionLayout.addWidget(docButton, 10)
        # self.optionLayout.setAlignment(QtCore.Qt.AlignCenter)
        optionLayout.setContentsMargins(0, 0, 0, 0)
        optionLayout.setSpacing(0)
        optionLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(optionLayout)
        # Stylesheet
        self.setStyleSheet("QWidget {margin: 0 0 0 0; padding: 0 0 0 0;} QPushButton{background:transparent; border:none; border-top: 2px solid #4da8e8; padding: 0 10px 0 10px; color: #ffffff; outline: none;} QPushButton:hover{background:#45c8dc;}")
        
        # Action
        # quitButton.clicked.connect(parent.close)
        docButton.clicked.connect(self.openDoc)

    def openDoc(self):
        
        winfullpathdir = os.getcwd().replace("/", "\\")  + "\\documentation\\Documentation.pdf"
        subprocess.Popen(r'explorer -p, %s'%winfullpathdir)

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
        # Click pos
        self.clickPos = QtCore.QPoint(50, 50)
        # Title font
        self.taskFont = QtGui.QFont('Segoe UI', 13)
        # Button font
        self.buttonFont = QtGui.QFont("Segoe UI")
        self.buttonFont.setPointSize(11)
        self.buttonFont.setBold(False)
        # Layout
        self.titleLayout = QtWidgets.QHBoxLayout()
        # Widgets
        self.taskLabel = QtWidgets.QLabel("")
        self.taskLabel.setMargin(5)
        self.taskLabel.setFont(self.taskFont)
        self.runButton = QtWidgets.QPushButton("Run")
        self.runButton.setFont(self.buttonFont)
        self.resetButton = QtWidgets.QPushButton("Reset")
        self.resetButton.setFont(self.buttonFont)
        self.stopButton = QtWidgets.QPushButton("Stop")
        self.stopButton.setFont(self.buttonFont)
        self.stopButton.setStyleSheet("QPushButton{background: #fa7064;border: 1px solid #f43f2f; outline: none;}QPushButton:hover{background: #f84e41;border: 1px solid #f73728;}QPushButton:disabled{background:#acb6ba; border:1px solid #5e7688; color:#fafbfc;}")
        # self.runButton.setDisabled(True)
        """
        self.resetButton.setEnabled(True)
        self.stopButton.setDisabled(True)
        """
        self.runButton.setVisible(False)
        self.resetButton.setVisible(False)
        self.stopButton.setVisible(False)
        self.minAppButton = QtWidgets.QToolButton()
        self.minAppButton.setIcon(QtGui.QIcon(":/resources/minimize.png"))
        self.minAppButton.setIconSize(QtCore.QSize(30, 30))
        self.maxAppButton = QtWidgets.QToolButton()
        self.maxAppButton.setIcon(QtGui.QIcon(":/resources/maximize.png"))
        self.maxAppButton.setIconSize(QtCore.QSize(30, 30))
        self.closeAppButton = QtWidgets.QToolButton()
        self.closeAppButton.setIcon(QtGui.QIcon(":/resources/close.png"))
        self.closeAppButton.setIconSize(QtCore.QSize(30, 30))

        # Add widgets
        self.titleLayout.insertStretch(0, 1)
        self.titleLayout.addWidget(self.taskLabel, 8)
        self.titleLayout.addWidget(self.runButton, 0.5)
        self.titleLayout.addWidget(self.resetButton, 0.5)
        self.titleLayout.addWidget(self.stopButton, 0.5)
        self.titleLayout.insertStretch(5, 1)
        """
        self.titleLayout.addWidget(self.minAppButton, 0.2)
        self.titleLayout.addWidget(self.maxAppButton, 0.2)
        self.titleLayout.addWidget(self.closeAppButton, 0.2)
        """
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
        self.normal_flag = True
        self.runButton.clicked.connect(self.Run)
        self.resetButton.clicked.connect(self.Reset)
        self.stopButton.clicked.connect(self.Stop)
        self.closeAppButton.clicked.connect(parent.close)
        self.minAppButton.clicked.connect(parent.showMinimized)
        self.maxAppButton.clicked.connect(self.switchMaximized)
                
    # From maximized to minimized
    def switchMaximized(self):
        
        if self.normal_flag:
        
            self.parent.showMaximized()
            self.maxAppButton.setIcon(QtGui.QIcon(":/resources/restore.png"))
        
        else:
            
            self.parent.showNormal()
            self.maxAppButton.setIcon(QtGui.QIcon(":/resources/maximize.png"))
        
        self.normal_flag = not self.normal_flag
        
    """    
    def mousePressEvent(self, event):
        
        if event.button() == QtCore.Qt.LeftButton:

            self.startPos = event.globalPos()
            self.clickPos = self.mapToParent(self.pos())
    
    
    # Move the frame    
    def mouseMoveEvent(self, event):
        
        if not self.normal_flag:
            
            return

        self.parent.move(event.globalPos() - self.clickPos)
    """    
        
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
        run_signal = self.currentTask.checkRun()
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
            self.currentContent.setLogColor("#fa7064")
            self.currentTask.printRun()
            self.currentContent.setLogNormalColor()
            self.childrenPanelStart = self.currentTask.panel_start
            for i in self.childrenPanelStart:
                
                self.currentPanel.item(i).setHidden(True)
                
            # self.currentIndex = self.parentWidget().parentWidget().sideBar.sideMenu.currentRow()
            # Disable the setting widget
            self.currentContent.mainStackWidget.widget(0).setEnabled(False)
            # Change the widget to the log and to the bottom
            self.currentPanel.setCurrentRow(1)
            # Disable left panel
            self.parent.sideWindow.sideMenu.setVisible(False)    
            self.parent.sideWindow.sideRunMenu.setVisible(True)
            # Call the widget's run function
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
            
            self.currentContent.setLogColor("#fa7064")
            sys.stdout.write("Stopping the task...")
            self.currentTask.Stop()
            self.Finish(0)
            sys.stdout.write("Task is stopped")    
            self.currentContent.setLogNormalColor()

          
    # Finish
    def Finish(self, finish_signal):
        
        # Enable setting
        self.currentContent.mainStackWidget.widget(0).setEnabled(True)
            
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
        self.mainContentWidget.mainSettingLayout.addWidget(self.taskWidget)
        # Nested widget
        # Design
        self.designcontentWidget = DesignContent(parent)
        self.designcontentWidget.setCurrentIndex(0)
        # Table
        self.tablecontentWidget = TableContent(parent)
        self.tablecontentWidget.setCurrentIndex(0)
        # Other
        self.othercontentWidget = OtherContent()
        self.othercontentWidget.setCurrentIndex(0)
        # Control panel
        self.contentPanel = MainContentPanel(self)
        self.contentPanel.setCurrentRow(-1)
        # Add widgets
        # Add an empty widget as initial
        self.taskWidget.addWidget(self.designcontentWidget)
        self.taskWidget.addWidget(self.tablecontentWidget)
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
        
    
    def showTask(self):
        
        self.mainContentWidget.setVisible(True) 
        
        
   

# Panel
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
        font = QtGui.QFont("Segoe UI", 10)
        self.logConsole.setFont(font)
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
        sys.stdout.textWritten.connect(self.writeLog)
        self.logClear_btn.clicked.connect(self.clearLog)
        # self.graph_comboBox.currentIndexChanged.connect(self.changeGraph)
        self.tableExport_btn.clicked.connect(self.exportTable)
        self.plotExport_btn.clicked.connect(self.exportPlot)


    # Write log
    def writeLog(self, text):
          
        self.logConsole.verticalScrollBar().setValue(self.logConsole.verticalScrollBar().maximum())        
        if "Error" in text or "Oops" in text:
            
            self.logConsole.setTextColor(QtGui.QColor("#66cc6e"))
            self.logConsole.append(text)
            self.logConsole.setTextColor(NORMAL_LOG_COLOR)
            
        else: 
           
            self.logConsole.append(text)
            
    
    # Set log color
    def setLogColor(self, color):
        
        self.logConsole.setTextColor(QtGui.QColor(color))        


    # Set log normal color
    def setLogNormalColor(self):
        
        self.logConsole.setTextColor(NORMAL_LOG_COLOR)


    # Clear log
    def clearLog(self):

        self.logConsole.verticalScrollBar().setValue(0)        
        self.logConsole.clear()

    
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
                
                index_name[i] = [column_names[i] + " " + str(cname) for cname in list(set(df.ix[:, i]))]
               
            n_index0 = len(index_name[0])
            n_index1 = len(index_name[1]) 
                
            # Use pivot to create table
            for j in column_valid:
                
                name = column_names[j]
                single_result = QtWidgets.QFrame()
                single_result.setMinimumHeight((n_index0 + 1) * 120 )
                single_result.setStyleSheet("QFrame{background:#f9fafc;font-family:'Segoe UI';border: 1px solid #f9fafc;border-radius: 5px; max-height:1000px;}")
                # Layout
                single_result_layout = QtWidgets.QVBoxLayout()
                # Title
                single_main_title = QtWidgets.QLabel()
                single_main_title.setText(name)
                single_main_title.setStyleSheet("QLabel{color:#7e888c; font-family:'Segoe UI'; font-size:11pt;}")
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
                single_main_table.setStyleSheet("QTableWidget{border: none; background:transparent; outline:none; gridline-color: #ffffff;} QTableWidget QTableCornerButton::section{background:#f7fafc; border: none;}  QHeaderView:Section{background:transparent; border:none; padding: 0 5px 5px 5px;} QTableWidget::item{border:none; color:#66cc6e; font-size: 12pt; font-family:'Segoe UI Light'; text-align:center;} QLineEdit{border: none; }")
                single_main_table.setRowCount(n_index0)
                single_main_table.setColumnCount(n_index1)
                single_main_table.setHorizontalHeaderLabels(index_name[1])
                single_main_table.setVerticalHeaderLabels(index_name[0])
                for k in range(n_index0):
                    
                    for m in range(n_index1):
                        
                        # Align at center
                        if pd.isnull(new_df.ix[k + 1, m + 1]):
                            
                            item = QtWidgets.QTableWidgetItem("-")
                            
                        else:
                            
                            item = QtWidgets.QTableWidgetItem(str(np.around(new_df.ix[k + 1, m + 1], 3)))
                        
                        # Disable edit
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                        item.setTextAlignment(QtCore.Qt.AlignCenter)
                        item.setFont(TABLE_CELL_FONT)
                        single_main_table.setItem(k, m, item)
                
                # single_main_table.resizeRowsToContents()
                # Add widget
                single_result_layout.addWidget(single_main_title)
                single_result_layout.addWidget(single_main_table)
                # Set layout
                single_result_layout.setContentsMargins(15, 30, 15, 30)
                single_result_layout.setSpacing(30)
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


class DesignContent(QtWidgets.QStackedWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QStackedWidget.__init__(self, parent)
        # Design widget
        self.mamsWidget = MAMS_Design(parent)
        self.addWidget(self.mamsWidget)



class TableContent(QtWidgets.QStackedWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QStackedWidget.__init__(self, parent)   
        # Critical value look-up table 
        self.criticalvalueWidget = CriticalValue_Table(parent)
        self.addWidget(self.criticalvalueWidget)    
         
         
         
class OtherContent(QtWidgets.QStackedWidget):
    
    
    def __init__(self, parent=None):
        
        QtWidgets.QStackedWidget.__init__(self, parent)
  
        
            
# Content
class MAMS_Design(QtWidgets.QWidget, Ui_MAMSWindow):
 
    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Setup ui
        self.setupUi(self)
        # Parent
        self.parent = parent
        # Initial variable
        # Title
        self.title = "Multi-Arm Multi-Stage Design"
        # Panel
        self.panel_start = [2, 3]
        self.panel_finish = [2, 3]
        # Flag for whether finish the task
        # 1 finished
        # 2 not finished
        self.finishflag = 0
        self.function_run = True
        # MAMS itself
        # Number of simulations
        self.nsim = 0
        # Seed
        self.seed = 0
        # Efficacy, futility
        self.eff = self.fut = 0
        # Clinically interesting difference
        self.clinSig = 0
        # Number of arms, number of stages, initial as 0
        self.nArm = self.nStage = 0
        # List for treatment effects, number of stages
        self.te_list = self.ns_list = []
        # Allocation ratio
        self.alloc = 0
        # Checkbox for adding patients to other treatment arms
        self.addPat = 0
        # Set predictive probability
        self.predict = 0
        self.predNum = 0
        self.predSuccess = 0
        self.preClinSig_flag = 0
        self.predClinSig = 0
        self.searchMethod = 0
        self.loadCVL = 0 
        self.CVLfile = ""
        # Old settings
        self.old_setting = ()
        # Flag for treatment effect and patient assignment
        self.trtEff_flag = self.patNum_flag = True

        # Set validator
        # Number of simulations
        self.sim_objValidator = QtGui.QIntValidator(self)
        self.sim_objValidator.setRange(1000, 100000)
        self.sim_textCtl.setValidator(self.sim_objValidator)
        # Seed
        self.seed_objValidator = QtGui.QIntValidator(self)
        self.seed_objValidator.setRange(1,99999)
        self.seed_textCtl.setValidator(self.seed_objValidator)
        # Futility
        self.fut_objValidator = StrictDoubleValidator()
        self.fut_objValidator.setRange(0.0, 0.999, 3)
        self.fut_textCtl.setValidator(self.fut_objValidator)
        # Efficacy
        self.eff_objValidator = StrictDoubleValidator()
        self.eff_objValidator.setRange(0.0, 0.999, 3)
        self.eff_textCtl.setValidator(self.eff_objValidator)
        # Clinical significant difference
        self.clinSig_objValidator = StrictDoubleValidator()
        self.clinSig_objValidator.setRange(0.0, 0.999, 3)
        self.clinSig_textCtl.setValidator(self.clinSig_objValidator)
        # Added patients
        self.predNum_objValidator = QtGui.QIntValidator(self)
        self.predNum_objValidator.setRange(1, 3000)
        self.predNum_textCtl.setValidator(self.predNum_objValidator)
        # Success boundary
        self.predSuccess_objValidator = StrictDoubleValidator(self)
        self.predSuccess_objValidator.setRange(0.0, 0.999, 3)
        self.predSuccess_textCtl.setValidator(self.predSuccess_objValidator)
        # Clinical significant difference for predictive probability calculation
        self.predClinSig_textCtl.setValidator(self.clinSig_objValidator)
        # Filter for combobox
        self.wheelfilter = WheelFilter()
        self.nArm_comboBox.installEventFilter(self.wheelfilter)
        self.nStage_comboBox.installEventFilter(self.wheelfilter)
        self.search_comboBox.installEventFilter(self.wheelfilter)
        # Font
        # header font
        self.headerFont = QtGui.QFont("Segoe UI")
        self.headerFont.setPointSize(10)
        self.headerFont.setBold(False)
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
        # Validator for allocation ratio
        self.ar_objValidator = TableARValidator(self)
        self.ar_objValidator.setRange(1.0, 4.0, 3)
        self.alloc_textCtl.setValidator(self.ar_objValidator)
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

        
        # Action
        # Binding functions
        self.seed_checkBox.toggled.connect(self.seed_textCtl.setEnabled)
        self.nArm_comboBox.currentIndexChanged.connect(self.setArm)
        self.nStage_comboBox.currentIndexChanged.connect(self.setStage)
        self.nArm_comboBox.currentIndexChanged.connect(self.resetEffSize)
        self.nStage_comboBox.currentIndexChanged.connect(self.resetPatNum)
        self.predict_checkBox.toggled.connect(self.setPredict)
        self.predict_checkBox.toggled.connect(self.predNum_textCtl.setEnabled)
        self.predict_checkBox.toggled.connect(self.predSuccess_textCtl.setEnabled)
        self.predict_checkBox.toggled.connect(self.checkClinical)
        self.predict_checkBox.toggled.connect(self.checkSelected)
        self.predClinSig_checkBox.toggled.connect(self.predClinSig_textCtl.setDisabled)
        self.search_comboBox.currentIndexChanged.connect(self.checkTable)
        self.loadCVL_checkBox.toggled.connect(self.loadCVL_textCtl.setEnabled)
        self.loadCVL_checkBox.toggled.connect(self.loadCVL_btn.setEnabled)
        self.predict_checkBox.toggled.connect(self.search_comboBox.setEnabled)
        
        self.loadCVL_btn.clicked.connect(self.loadCVLFile)
        self.trtEffSize_btn.clicked.connect(self.switchEffSize)
        self.assignPatient_btn.clicked.connect(self.switchPatNum)
        self.saveEff_btn.clicked.connect(self.saveEffSize)
        self.resetEff_btn.clicked.connect(self.resetEffSize)
        self.cancelEff_btn.clicked.connect(self.switchEffSize)
        self.savePat_btn.clicked.connect(self.savePatNum)
        self.resetPat_btn.clicked.connect(self.resetPatNum)
        self.cancelPat_btn.clicked.connect(self.switchPatNum)
        

    # Set number of arms
    def setArm(self):
          
        index = self.nArm_comboBox.currentIndex()
        if index != -1:
            
            value = int(str(self.nArm_comboBox.currentText()))
            if self.nStage_comboBox.currentIndex() != -1:
                
                self.assignPatient_btn.setEnabled(True)
            
            self.trtEffSize_btn.setEnabled(True)
            if self.nArm and value != self.nArm:
            
                sys.stdout.write("Selected number of  treatment arms changed from %d to %d"%(self.nArm, value))
                self.nArm = value
                # Treatment effective size set to empty: Need to reset the treatment effective size
                
                if self.te_list: 
                
                    self.te_list = []
                    sys.stdout.write("Reset treatment effective size")
            
            elif not self.nArm:
            
                self.nArm = value
                sys.stdout.write("Selected number of treatment arms: %d" %value)


    # Set number of stages
    def setStage(self):

        index = self.nStage_comboBox.currentIndex()
        if index != -1:
            value = int(str(self.nStage_comboBox.currentText()))
            if self.nArm_comboBox.currentIndex() != -1:
            
                self.assignPatient_btn.setEnabled(True)
            
            if self.nStage and value != self.nStage:
                      
                sys.stdout.write("Selected number of stages changed from %d to %d"%(self.nStage, value))
                self.nStage = value
                
                if self.ns_list:
                
                    self.ns_list = []
                    sys.stdout.write("Reset number of patients at each stage")
            
            elif not self.nStage:
            
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


    # Load CVL for posterior predictive probability 
    def loadCVLFile(self):
        
        self.CVLfile, file_ilter = QtWidgets.QFileDialog.getOpenFileName(self, "Load CVL Table", "", self.tr("CSV(*.csv)"))
        sys.stdout.write("Load critical value lookup table:")
        sys.stdout.write("File location: %s" %self.CVLfile)
        self.loadCVL_textCtl.setText(self.CVLfile)


    # Check selected
    def checkSelected(self):

        if self.predict_checkBox.isChecked():
            
            self.predNum_textCtl.setEnabled(True)
            self.predSuccess_textCtl.setEnabled(True)
            self.predClinSig_textCtl.setEnabled(True)
            self.predClinSig_checkBox.setEnabled(True)
            if self.predClinSig_checkBox.isChecked():
                
                self.predClinSig_textCtl.setEnabled(False)
            
            if self.search_comboBox.currentIndex() != 0:
            
                self.loadCVL_checkBox.setEnabled(True)
                if self.loadCVL_checkBox.isChecked():
                       
                    self.loadCVL_textCtl.setEnabled(True)
                    self.loadCVL_btn.setEnabled(True)

        else:
            
            self.predNum_textCtl.setEnabled(False)
            self.predSuccess_textCtl.setEnabled(False)
            self.predClinSig_textCtl.setEnabled(False)
            self.predClinSig_checkBox.setEnabled(False)
            self.loadCVL_checkBox.setEnabled(False)
            self.loadCVL_textCtl.setEnabled(False)
            self.loadCVL_btn.setEnabled(False)
    
    
    # Check clinical
    def checkClinical(self):
        
        if self.predClinSig_checkBox.isChecked():
                
            self.predClinSig_textCtl.setEnabled(False)
        
        else:
            
            self.predClinSig_textCtl.setEnabled(True)
             

    # Check widgets for loadcvl
    def checkTable(self, index):

        if index == 1:
                
            self.loadCVL_checkBox.setEnabled(True)
            if self.loadCVL_checkBox.isChecked():
            
                self.loadCVL_textCtl.setEnabled(True)
                self.loadCVL_btn.setEnabled(True)

        else:

            self.loadCVL_checkBox.setChecked(False)
            self.loadCVL_checkBox.setEnabled(False)
            self.loadCVL_textCtl.setEnabled(False)
            self.loadCVL_btn.setEnabled(False)


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
            
            self.nArm_comboBox.setEnabled(True)
            

        self.trtEff_Frame.setVisible(self.trtEff_flag)
        self.trtEff_flag = not self.trtEff_flag


    # Switch patient frame
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
               
                self.alloc_textCtl.setText("%.3f"%(self.alloc)) 
                for j in range(self.nStage):
                
                    self.patNum_tableWidget.setItem(0, j, QtWidgets.QTableWidgetItem(str(int(self.ns_list[j]))))
            
            self.nStage_comboBox.setEnabled(False)
            self.nArm_comboBox.setEnabled(False)
        
        else:
            
            self.nStage_comboBox.setEnabled(True)
            self.nArm_comboBox.setEnabled(True)
            
        
        self.patNum_Frame.setVisible(self.patNum_flag)
        self.patNum_flag = not self.patNum_flag
        

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
        self.trtEff_Frame.setVisible(False)
        self.nArm_comboBox.setEnabled(True)

      
    # Reset effective size
    def resetEffSize(self):

        for i in range(self.nArm):
            
            self.effSize_tableWidget.setItem(0, i, None)
          
        self.effSize_tableWidget.setCurrentCell(-1, -1)
        self.te_list = []
        sys.stdout.write("Reset treatment effective size")
        # self.trtEff_flag = True
        # self.trtEff_Frame.setVisible(False)


    # Save effective size
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
        self.nArm_comboBox.setEnabled(True)
        self.nStage_comboBox.setEnabled(True)

    
    # Reset effective size
    def resetPatNum(self):

        sys.stdout.write("Reset allocation ratio")
        sys.stdout.write("Unset adding patients to other treatment arms when dropped")
        for i in range(self.nStage):
        
                self.patNum_tableWidget.setItem(0, i, None)
        
        self.patNum_tableWidget.setCurrentCell(-1, -1)
        self.ns_list = []
        sys.stdout.write("Reset number of patients at each stage")
        # self.patNum_flag = True
        # self.patNum_Frame.setVisible(False)


    # Run the trial
    def checkRun(self):

        try:
            
            self.nsim = int(self.sim_textCtl.text())
            if self.nsim > 100000 or self.nsim < 1000:
                
                msgBox = MessageBox()
                msgBox.setText("The number of simulations should between 1000 and 100000")
                msgBox.setWindowTitle("Missing Input")
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
            
            self.seed = 0

        if self.nArm_comboBox.currentIndex() == -1:
            
            msgBox = MessageBox()
            msgBox.setText("The number of arms has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nArm_comboBox.setFocus()
            return
        
        self.nArm = int(str(self.nArm_comboBox.currentText()))

        if self.nStage_comboBox.currentIndex() == -1:
            
            msgBox = MessageBox()
            msgBox.setText("The number of stage has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nStage_comboBox.setFocus()
            return
        
        self.nStage = int(str(self.nStage_comboBox.currentText()))

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
        
        if np.sum(self.ns_list) + self.predNum > 10000 :
            
            msgBox = MessageBox()
            msgBox.setText("Currently the total patients could not exceed 10000!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.patNum_flag = True
            self.switchPatNum()
            self.patNum_tableWidget.setFocus()
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
        
        # Futility, efficacy, clinical significant difference
        try:
            
            self.fut = float(self.fut_textCtl.text())
        
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The futility boundary has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.fut_textCtl.setFocus()
            return

        try:
            
            self.eff = float(self.eff_textCtl.text())
            if self.eff <= self.fut:
            
                msgBox = MessageBox()
                msgBox.setText("Efficacy boundary should be larger than futility boundary!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.eff_textCtl.setFocus()
                return
            
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The efficacy boundary has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.eff_textCtl.setFocus()
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
            
            try:
            
                self.predNum = int(self.predNum_textCtl.text())
            
            except:
            
                msgBox = MessageBox()
                msgBox.setText("The patients added has not been set!")
                msgBox.setWindowTitle("Missing Input")
                msgBox.exec_()
                self.predNum_textCtl.setFocus()
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
            
            
            self.searchMethod = int(self.search_comboBox.currentIndex() + 1)
            if self.searchMethod == 0:
                    
                self.searchMethod = 1
                sys.stdout.write("Use the default method (Bisection) to calculate the critical value")
            
            if self.searchMethod == 2 and self.loadCVL_checkBox.isChecked():
                
                self.loadCVL = 1
                if self.CVLfile == "":
                         
                    msgBox = MessageBox()
                    msgBox.setText("The critical value lookup table has not been impoted!")
                    msgBox.setWindowTitle("Missing Input")
                    msgBox.exec_()
                    self.loadCVL_btn.setFocus()
                    return         
            
            elif self.searchMethod == 2:
                
                self.loadCVL = 0
                self.CVLfile = ""      
                
        else:
            
            self.predict = 0
            self.predNum = 0
            self.predSuccess = 0
            self.predClinSig = 0
            self.searchMethod = 0          
            self.loadCVL = 0
            self.CVLfile = ""
        
        if self.old_setting == (self.nsim, self.seed, self.nArm, self.nStage, self.te_list, self.ns_list, 
                                self.alloc, self.eff, self.fut,  self.clinSig, 
                                self.predNum, self.predSuccess, self.predClinSig, self.searchMethod, self.CVLfile):
            
            msgBox = MessageBox(None, 2)
            msgBox.setText("All the settings are the same as last run. Do you want to run it again?")
            msgBox.setWindowTitle("Run the same scenario")
            result = msgBox.exec_()
            if result:
                
                return 2 
            
            else:
                
                return
        
        return 1
    
        
    # Print the settings of the run
    def printRun(self):
        
        # Number of simulations, seed
        sys.stdout.write("\nSimulation settings:")
        sys.stdout.write("# of simulations: %d"%(self.nsim))
        if self.seed_checkBox.isChecked():
            
            sys.stdout.write("The seed is set: %d"%(self.seed))
        
        else:
        
            sys.stdout.write("The seed is not set, a random seed is used")
        
        # Treatment effective size
        sys.stdout.write("\nTreatment effective size:")
        df_te_list = pd.DataFrame(np.array(self.te_list).reshape(1, self.nArm), index = ["Effective Size"], columns = self.effColHeaders)
        sys.stdout.write(df_te_list)
        
        # Patient at each stage
        sys.stdout.write("\nPatients at each stage:")   
        df_ns_list = pd.DataFrame(np.array(self.ns_list).reshape(1, self.nStage), index = ["# of Patients"],  columns = self.patColHeaders)      
        sys.stdout.write(df_ns_list)
        
        # Allocation ratio
        sys.stdout.write("\nAllocation ratio: %.3f"%self.alloc)
        
        # Futility, efficacy, clinical significant difference
        sys.stdout.write("\nFutility boundary:%.3f"%(self.fut))
        sys.stdout.write("Efficacy boundary:%.3f"%(self.eff))
        sys.stdout.write("Clinically significant difference:%.3f"%(self.clinSig))
        
        # If predictive probability is calculated
        if self.predict_checkBox.isChecked():
            
            sys.stdout.write("\nCalculate posterior predictive probability: Yes")
            sys.stdout.write("New # of patients added:%d"%self.predNum)
            sys.stdout.write("Success boundary:%.3f\n"%(self.predSuccess))
            sys.stdout.write("Clinical significant difference:%.3f\n"%(self.predClinSig))
            if self.searchMethod == 1:
                
                sys.stdout.write("Use bisection algorithm to create a critical value lookup table")
                
            else:
                
                sys.stdout.write("Create a whole critical value lookup table")
                 
            if self.loadCVL == 1:
                
                sys.stdout.write("Import critical lookup table from: %s"%(self.CVLfile))
            
            if self.searchMethod == 2 and self.loadCVL == 0:
                
                sys.stdout.write("Create a new critical lookup table")
        
        
    # Run 
    def Run(self):
        
        self.finishflag = 0        
        # Start thread
        try:
            
            # Create thread
            self.newfoldername = uuid.uuid4()
            self.pathdir = "./tmp/%s/" %self.newfoldername
            self.fullpathdir = str(os.getcwd()).replace("\\", "/") + self.pathdir[1:]
            # Main folder
            sys.stdout.write("Create folder for the simulation results")
            os.makedirs(self.pathdir)         
            # Append to the file
            trial_setting_file = open("%s/SimulationSetting.txt"%(self.pathdir), "a")
            # Write settings to the output file
            trial_setting_file.write("Simulation settings:\n")
            trial_setting_file.write("\n# of simulations: %d\n"%(self.nsim))
            if self.seed_checkBox.isChecked():
            
                trial_setting_file.write("The seed is set: %d\n"%(self.seed))
        
            else:
        
                trial_setting_file.write("The seed is not set, a random seed is used\n")
                
            trial_setting_file.write("\nTreatment effective size:\n")
            trial_setting_file.write("\t".join(self.effColHeaders) + "\n")
            trial_setting_file.write("\t".join(map(str, self.te_list)) + "\n")
            trial_setting_file.write("\nPatients at each stage:\n")  
            trial_setting_file.write("\t".join(self.patColHeaders) + "\n") 
            trial_setting_file.write("\t".join(map(str, self.ns_list)) + "\n")
            trial_setting_file.write("\nAllocation ratio: %.3f\n"%self.alloc)
            trial_setting_file.write("\nFutility boundary:%.3f\n"%(self.fut))
            trial_setting_file.write("Efficacy boundary:%.3f\n"%(self.eff))
            trial_setting_file.write("Clinically significant difference:%.3f\n"%(self.clinSig))
            if self.predict_checkBox.isChecked():
              
                trial_setting_file.write("\nCalculate posterior predictive probability: Yes\n")
                trial_setting_file.write("New # of patients added:%d\n"%self.predNum)
                trial_setting_file.write("Success boundary:%.3f\n"%(self.predSuccess))
                trial_setting_file.write("Clinically significant difference:%.3f\n"%(self.predClinSig))
            
            if self.searchMethod == 1:
                
                trial_setting_file.write("Use bisection algorithm to create a critical value lookup table\n")
                
            else:
                
                trial_setting_file.write("Create a whole critical value lookup table\n")
                 
            if self.loadCVL == 1:
                
                trial_setting_file.write("Import critical lookup table from: %s\n"%(self.CVLfile))
            
            if self.searchMethod == 2 and self.loadCVL == 0:
                
                trial_setting_file.write("Create a new critical lookup table\n")
            
            trial_setting_file.close()
                        
            self.function_run = True
            while self.function_run:
                
                self.finishflag = FixedTrial.TrialSimulation(self.pathdir, self.effColHeaders, 
                                    self.patColHeaders, self.nsim, self.seed, self.nArm, self.nStage, self.te_list, 
                                    self.ns_list, self.alloc, self.eff, self.fut,  self.clinSig, self.predict, 
                                    self.predNum, self.predSuccess, self.predClinSig, self.searchMethod, self.loadCVL, self.CVLfile)
                
                self.function_run = False                
       
            if self.finishflag == 0:  
               
                sys.stdout.write("Simulation finished...")
                self.parent.mainTitle.Finish(1)
                        
            else:
                
                sys.stdout.write("Oops, simulation failed...")
                self.finishflag = 0
                self.parent.mainTitle.Finish(0)
                shutil.rmtree(self.fullpathdir)
                
        except:
            
            exctype,excvalue = sys.exc_info()[:2]
            sys.stdout.write("Error: %s %s" %(str(exctype), str(excvalue)))
            shutil.rmtree(self.fullpathdir)
            self.parent.mainTitle.Finish(0)
        
        self.old_setting = (self.nsim, self.seed, self.nArm, self.nStage, self.te_list, self.ns_list, 
                            self.alloc, self.eff, self.fut,  self.clinSig, 
                            self.predNum, self.predSuccess, self.predClinSig, self.searchMethod, self.CVLfile)
        
        self.finishflag = 1
     
    # Reset the whole trial simulator
    def Reset(self):

        # Reset all the trial settings
        self.nsim = self.seed = self.nArm = self.nStage = self.eff = self.fut = self.clinSig = 0
        self.sim_textCtl.clear()
        self.seed_checkBox.setChecked(False)
        self.seed_textCtl.clear()
        self.nArm_comboBox.setCurrentIndex(-1)
        self.nStage_comboBox.setCurrentIndex(-1)
        self.eff_textCtl.clear()
        self.fut_textCtl.clear()
        self.alloc_textCtl.clear()
        self.clinSig_textCtl.clear()
        # Reset all the predictive probabilities
        self.predict = self.predNum = self.predSuccess = self.predClinSig = self.searchMethod = self.loadCVL = 0
        self.CVLfile = ""
        self.predict_checkBox.setChecked(False)
        self.predNum_textCtl.clear()
        self.predSuccess_textCtl.clear()
        self.predClinSig_checkBox.setChecked(False)
        self.search_comboBox.setCurrentIndex(-1)
        self.loadCVL_checkBox.setChecked(False)
        self.loadCVL_textCtl.clear()
        # Reset treatment effective sizes and number of patients
        if self.te_list:
            
            self.resetEffSize()
            
        if self.ns_list:
                       
            self.resetPatNum()
        
   
    # Stop
    def Stop(self):
        
        self.function_run = False
        self.finishflag = 0
    
    # Write result to table
    def setResult(self):
        
        self.finalresultfile = self.fullpathdir + "/FinalResult.csv"
        self.fileindex = [0, 1]
        self.currentContent = self.parent.mainContent.mainContentWidget
        self.currentContent.setCallbackResult(self.finalresultfile, self.fileindex)
        
    # Write the plot
    def setPlot(self):
        
        self.currentContent.setCallbackPlot(self.fullpathdir)
      
        
    
# Critical value table
class CriticalValue_Table(QtWidgets.QWidget, Ui_CriticalValueTableWindow):

    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Title
        self.title = "Critical Value Look-up Table"
        # Parent
        self.parent = parent
        # Panel
        self.panel_start = [2, 3]
        self.panel_finish = []
        # Finish flag
        self.finishflag = 0
        self.function_run = True
        # Setup ui
        self.setupUi(self)
        # Seed
        self.seed = 0
        # Clinically significant difference
        self.clinSig = 0
        # Number of patients
        self.n1 = self.n2 = 0
        # Output directory
        self.CVLfile = ""
        # Tuple to store old settings
        self.old_setting = ()
        # Set validator
        # Seed
        self.seed_objValidator = QtGui.QIntValidator(self)
        self.seed_objValidator.setRange(1,999999)
        self.seed_textCtl.setValidator(self.seed_objValidator)
        # Clinical significant difference
        self.clinSig_objValidator = StrictDoubleValidator()
        self.clinSig_objValidator.setRange(0.0, 0.999, 3)
        self.clinSig_textCtl.setValidator(self.clinSig_objValidator)
        # Added patients
        self.nPatient_objValidator = QtGui.QIntValidator(self)
        self.nPatient_objValidator.setRange(1, 2500)
        self.nTreatment_textCtl.setValidator(self.nPatient_objValidator)
        self.nControl_textCtl.setValidator(self.nPatient_objValidator)
        
        # Binding functions
        self.seed_checkBox.toggled.connect(self.seed_textCtl.setEnabled)
        self.saveCVL_btn.clicked.connect(self.saveCVLFile)
        
        
    def saveCVLFile(self):
               
        self.CVLfile, filetype = QtWidgets.QFileDialog.getSaveFileName(self, "Save CVL to...", "", self.tr("CSV(*.csv)"))
        self.saveCVL_textCtl.setText(self.CVLfile)
        
        
    def checkRun(self):
    
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
            
            self.seed = 0

        try:
            
            self.clinSig = float(self.clinSig_textCtl.text())
                
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The clinically significant difference has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.clinSig_textCtl.setFocus()
            return
        
        
        try:
            
            self.n1 = int(self.nTreatment_textCtl.text())
                
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The number of patients in treatment has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nTreatment_textCtl.setFocus()
            return
        
        
        try:
            
            self.n2 = int(self.nControl_textCtl.text())
                
        except:
            
            msgBox = MessageBox()
            msgBox.setText("The number of patients in control has not been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.nControl_textCtl.setFocus()
            return
        
        
        if self.CVLfile == "":
            
            msgBox = MessageBox()
            msgBox.setText("Output directory has bot been set!")
            msgBox.setWindowTitle("Missing Input")
            msgBox.exec_()
            self.saveCVL_btn.setFocus()
            return
        
        
        if self.old_setting == (self.seed, self.clinSig, self.n1, self.n2):
            
            msgBox = MessageBox(None, 2)
            msgBox.setText("All the settings are the same as last run. Do you want to run it again?")
            msgBox.setWindowTitle("Run the same scenario")
            result = msgBox.exec_()
            if result:
                
                return 2
            
            else:
                
                return
            
        return 1
    
    
    # Print the setting of the run
    def printRun(self):
        
        sys.stdout.write("\nCritical look-up table settings:")
        if self.seed_checkBox.isChecked():
            
            sys.stdout.write("The seed is set: %d"%(self.seed))
        
        else:
        
            sys.stdout.write("The seed is not set, a random seed is used")
        
        # Number of patient in treatment arm
        sys.stdout.write("\n#Patients in Treatment:%d"%(self.n1))
        sys.stdout.write("#Patients in Control:%d"%(self.n2))
        sys.stdout.write("Clinically significant difference:%.3f"%(self.clinSig))
        sys.stdout.write("Output critical lookup table to: %s"%(self.CVLfile))
    
    
    def Run(self):
        
        self.finishflag = 0
        sys.stdout.write("\nStart creating table...")
        try:
        
            self.function_run = True
            while self.function_run:
            
                self.finishflag = CreateCriticalValueTable.NewCriticalValueTable(self.seed,
                                self.n1, self.n2, self.clinSig, self.CVLfile)
        
                self.function_run = False
                
            if self.finishflag == 0:
                
                sys.stdout.write("Table creation finished...")
                self.parent.mainTitle.Finish(1)
                
            else:
                
                sys.stdout.write("Oops, table creation failed")
                self.finishflag = 0
                self.parent.mainTitle.Finish(0)
                
        except:
            
            exctype,excvalue = sys.exc_info()[:2]
            sys.stdout.write("Error: %s %s" %(str(exctype), str(excvalue)))
            self.parent.mainTitle.Finish(0)
            
            
        self.old_setting = (self.seed, self.clinSig, self.n1, self.n2)  
        self.finishflag = 1
    
    
    def Reset(self):
        
        msgBox = MessageBox(None, 2)
        msgBox.setText("Are you sure you want to reset all the settings?")
        msgBox.setWindowTitle("Reset the critical value generating settings")
        result = msgBox.exec_()
        if result:
        
            sys.stdout.write("Reset all the settings")
            # Reset all the trial settings
            self.seed = self.clinSig = self.n1 = self.n2 =  0
            self.seed_checkBox.setChecked(False)
            self.seed_textCtl.clear()
            self.clinSig_textCtl.clear()
            self.nTreatment_textCtl.clear()
            self.nControl_textCtl.clear()
            self.CVLfile = ""
            self.saveCVL_textCtl.clear()
            self.runTable_btn.setEnabled(True) 
    
    
    def Stop(self):
        
        self.function_run = False
        self.finishflag = 0
        
    
    
# Titlebar for all the sub windows
class SubTitleBar(QtWidgets.QWidget):
    
    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        # Click pos
        self.clickPos = QtCore.QPoint(50, 50)
        # App Icon
        self.icon_Label = QtWidgets.QLabel()
        self.icon_Label.setPixmap(QtGui.QPixmap(":/resources/bcts.png").scaled(QtCore.QSize(40, 40)))
        self.icon_Label.setFixedWidth(40)
        # Title font
        self.title_font = QtGui.QFont("Segoe UI")
        self.title_font.setPointSize(11)
        self.title_font.setBold(True)
        # Title        
        self.title_Label = QtWidgets.QLabel("")
        self.title_Label.setFont(self.title_font)
        self.title_Label.setAlignment(QtCore.Qt.AlignCenter)
        #　Button
        self.closeApp_btn = QtWidgets.QToolButton()
        self.closeApp_btn.setIcon(QtGui.QIcon(":/resources/close.png"))
        self.closeApp_btn.setObjectName("closeButton")
        self.titlelayout = QtWidgets.QHBoxLayout()
        self.titlelayout.addWidget(self.icon_Label)
        self.titlelayout.addWidget(self.title_Label)
        self.titlelayout.addWidget(self.closeApp_btn)
        self.titlelayout.setSpacing(0) 
        self.titlelayout.setContentsMargins(5, 5, 5, 5)
        # Stylesheet
        self.setStyleSheet("QLabel{background:#ffffff; color:#859ba6; font-family:'Segoe UI'; font-size:12pt;} QToolButton{border:none;} QPushButton:hover{background:#6e66cc;border:1px solid #373366;} QToolButton:hover{background:#fa7064;}")
        self.setLayout(self.titlelayout)
        # Slots & signals
        self.closeApp_btn.clicked.connect(parent.close)

    def mousePressEvent(self, event):
        
        if event.button() == QtCore.Qt.LeftButton:

            self.startPos = event.globalPos()
            self.clickPos = self.mapToParent(self.pos())
    
    # Move the frame    
    def mouseMoveEvent(self, event):

        self.parentWidget().move(event.globalPos() - self.clickPos)
       
        

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




# Validator for futile, effifcacy and clinical significant difference
class StrictDoubleValidator(QtGui.QDoubleValidator):

    def __init__(self, parent = None):

        QtGui.QDoubleValidator.__init__(self, parent)
        self.setNotation(QtGui.QDoubleValidator.StandardNotation)


    def validate(self, input, pos):

        state, input, pos = QtGui.QDoubleValidator.validate(self, input, pos)
        if state == QtGui.QValidator.Invalid:
            
            return (QtGui.QValidator.Invalid, input, pos)
        
        if pos == 1:
        
            try: 
                
                if float(str(input)) >= 1:
                    
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos == 2:
            
            if not str(input)[pos-1] == ".":
                
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos > 2:
        
            try:
                
                if  float(str(input)) >= 1:
                    
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                return (QtGui.QValidator.Invalid, input, pos)
        
        return (QtGui.QValidator.Acceptable, input, pos)



# Validator for table entry, rewrite the table
class TableDoubleValidator(QtWidgets.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtWidgets.QLineEdit(widget)
        self.cell_validator = StrictDoubleValidator()
        self.cell_validator.setRange(0.0, 0.999, 3)
        self.cellEditor.setValidator(self.cell_validator)

        return self.cellEditor



# Validator for allocation ratio
class TableARValidator(QtGui.QDoubleValidator):

    def __init__(self, parent = None):

        QtGui.QDoubleValidator.__init__(self, parent)
        self.setNotation(QtGui.QDoubleValidator.StandardNotation)

    def validate(self, input, pos):

        state, input, pos = QtGui.QDoubleValidator.validate(self, input, pos)
        if state == QtGui.QValidator.Invalid:
        
            return (QtGui.QValidator.Invalid, input, pos)
        
        if pos == 1:
        
            try: 
                
                if float(str(input)) > 4:
                    
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos == 2:
        
            if not str(input)[pos-1] == ".":
                
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos > 2:
            
            try:
                
                if  float(str(input)) >= 4:
                    
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                return (QtGui.QValidator.Invalid, input, pos)
        
        return (QtGui.QValidator.Acceptable, input, pos)


# Validator for patients assignments
# Will be used in version 1 and version 2
class TableIntValidator(QtWidgets.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtWidgets.QLineEdit(widget)
        self.cell_validator = QtGui.QIntValidator(self)
        self.cell_validator.setRange(10, 2000)
        self.cellEditor.setValidator(self.cell_validator)
        
        return self.cellEditor
        
        

# Std write out
class StdOutStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        
        self.textWritten.emit(str(text))
        QtCore.QCoreApplication.processEvents()
    
    def flush(self):
    
        pass



# Message box
class MessageBox(QtWidgets.QDialog):

    def __init__(self, parent=None, type = 1):

        QtWidgets.QDialog.__init__(self, parent)
        # Type 1: OK default
        # Type 2: Yes|No
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.resize(400, 250)
        # self.title = self.windowTitle()
        self.msgLayout = QtWidgets.QVBoxLayout()
        self.msgLabelLayout = QtWidgets.QHBoxLayout()
        self.msgButtonLayout = QtWidgets.QHBoxLayout()
        self.msgButtonLayout.setAlignment(QtCore.Qt.AlignRight)
        self.subtitlebar = SubTitleBar(self)
        self.msg_Label = QtWidgets.QLabel("")
        self.msg_Label.setObjectName("MessageLabel")
        self.msg_Label.setMargin(5)
        self.msg_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.msgLabelLayout.setContentsMargins(0, 0, 0, 0)
        self.msgLabelLayout.setAlignment(QtCore.Qt.AlignCenter)
        # Add layout
        self.msgLabelLayout.addWidget(self.msg_Label)
        self.hline = QtWidgets.QWidget()
        self.hline.setObjectName("MessageLine")
        self.hline.setWindowOpacity(0.5)
        self.msgYes_btn = QtWidgets.QPushButton("Yes")
        self.msgNo_btn = QtWidgets.QPushButton("No")
        self.msgOK_btn = QtWidgets.QPushButton("OK")

        if type == 1:

            self.msgButtonLayout.addWidget(self.msgOK_btn, 3)

        else:

            self.msgButtonLayout.addWidget(self.msgYes_btn, 3)
            self.msgButtonLayout.addWidget(self.msgNo_btn, 3)

        self.msgLayout.addWidget(self.subtitlebar, 2)
        self.msgLayout.addWidget(self.hline, 1)
        self.msgLayout.addLayout(self.msgLabelLayout, 7)
        self.msgButtonLayout.setSpacing(5)
        self.msgButtonLayout.setContentsMargins(5, 0, 5, 15)
        self.msgLayout.addLayout(self.msgButtonLayout)
        self.msgLayout.setSpacing(0)
        self.msgLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.msgLayout)
        self.setStyleSheet("QDialog {background: #ffffff; border: none; font-family:'Segoe UI'; font-size:12pt;} QWidget#MessageLine{max-height:2px; width:100%; background:#399ee5;} QLabel#MessageLabel{font-family:'Segoe UI'; font-size:12pt; color:#3d5159;} QPushButton{background: #66cc6e; color: #ffffff; font-family:'Segoe UI'; font-size:12pt; border-radius: 5px; border: 1px solid #4bae54; padding:5px 15px 5px 15px; margin:5px 5px 10px 5px; max-width: 100px;} QPushButton:hover{background: #6e66cc;border:1px solid #373366;} ")
        # Connect functions
        self.msgOK_btn.clicked.connect(self.close)
        self.msgYes_btn.clicked.connect(self.accept)
        self.msgNo_btn.clicked.connect(self.reject)

        # Beep sound
        QtWidgets.QApplication.beep()

    # Rewrite the functions
    def setWindowTitle(self, text):

        self.subtitlebar.title_Label.setText(text)

    def setText(self, text):

        self.msg_Label.setText(text)



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



# Event filter
# Disable scroll on comboBox
class WheelFilter(QtCore.QObject):
    
    def eventFilter(self, source, event):
        
        if event.type() == QtCore.QEvent.Wheel:
             
            return True
    
        return False



# Init
if __name__ == '__main__':

    # Set id
    import ctypes
    appid = u'bats.1.0' # arbitrary string
    
    if sys.platform == 'win32':

       ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    
    elif sys.platform == 'linux2':

       pass
    
    else:
      
      sys.stdout.write("The application is not supported in this system")
      pass
    
    app = QtWidgets.QApplication(['Bayesian Adaptive Trial Simulator'])
    app_icon = QtGui.QIcon()
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(16,16))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(24,24))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(32,32))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(48,48))
    app_icon.addFile(":/resources/bcts.png", QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)
    # Splashscreen of the application
    # movie = QtGui.QMovie(":/resources/splashfade.gif")
    # splash = MovieSplashScreen(movie)
    # splash.show()
    # app.processEvents()
    # Display the animation
    # start = time.time()
    # while movie.state() == QtGui.QMovie.Running and time.time() < start + 5:
    #     app.processEvents()
    # Load font
    QtGui.QFontDatabase().addApplicationFont(":/resources/font/Caviar_Dreams_Bold.ttf")
    QtGui.QFontDatabase().addApplicationFont(":/resources/font/PTsans.ttf")
    window = ApplicationWindow()
    window.show()
    # splash.finish(window)
    # Maximize the application window
    # window.showMaximized()
    app.exec_()

