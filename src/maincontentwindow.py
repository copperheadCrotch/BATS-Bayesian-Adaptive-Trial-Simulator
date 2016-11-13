# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainContentWindow.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainContentWindow(object):
    def setupUi(self, MainContentWindow):
        MainContentWindow.setObjectName("MainContentWindow")
        MainContentWindow.resize(1000, 761)
        self.gridLayout_4 = QtWidgets.QGridLayout(MainContentWindow)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.mainStackWidget = QtWidgets.QStackedWidget(MainContentWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainStackWidget.sizePolicy().hasHeightForWidth())
        self.mainStackWidget.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(10)
        self.mainStackWidget.setFont(font)
        self.mainStackWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.mainStackWidget.setStyleSheet("QWidget{\n"
"     background:#ffffff;\n"
"}\n"
"\n"
"QLabel{\n"
"    color:#399ee5;\n"
"    background: transparent;\n"
"}\n"
"\n"
"QLineEdit{\n"
"     font-family:\'Segue UI Emoji\';\n"
"     font-size: 10pt;\n"
"     border: 1px solid #c5d2d9; \n"
"     border-radius:5px;\n"
"     background:#ffffff;\n"
"     padding: 5px 10px 5px 10px; \n"
"     color: #66767c;\n"
"     min-width: 180px;\n"
"     max-width: 180px;\n"
"}\n"
"\n"
"QLineEdit:disabled{\n"
"    background: #b2bbbf;\n"
"    border: 1px solid #acb6ba;\n"
"    color: #b2bbbf;\n"
"}\n"
"\n"
"QLineEdit:placeholder:disabled{\n"
"    color: #8497a5     ;\n"
"}\n"
"\n"
"QCheckBox{\n"
"     color:#399ee5;\n"
"     min-height: 5px;\n"
"}\n"
"\n"
"QCheckBox::indicator{\n"
"     border: 1px solid #399ee5;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked{\n"
"     padding: 1px 1px 1px 1px;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked{\n"
"     background:#399ee5;\n"
"     background-origin: content;\n"
"     background-clip: content;\n"
"}\n"
"\n"
"\n"
"QCheckBox::indicator:disabled{\n"
"     background: #b2bbbf;\n"
"    border: 1px solid #acb6ba;\n"
"}\n"
"\n"
"QComboBox{\n"
"     font-family:\'Segue UI Emoji\';\n"
"     font-size: 10pt;\n"
"     border: 1px solid #c5d2d9; \n"
"     border-radius:5px;\n"
"     padding: 5px 10px 5px 10px; \n"
"     color: #66767c;\n"
"     min-width: 180px;\n"
"     max-width: 180px;\n"
"}\n"
"\n"
"QComboBox:hover{\n"
"     border: 2px solid #2a4d69;\n"
"     border-radius: 5px;\n"
"     height: 30ps;\n"
"}\n"
"\n"
"QComboBox:disabled{\n"
"    background: #b2bbbf;\n"
"    border: 1px solid #acb6ba;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 40px;\n"
"    border-left-width: 2px;\n"
"    border-left-color: #c5d2d9;\n"
"    border-left-style: solid; /* just a single line */\n"
"    border-top-right-radius: 5px; /* same radius as the QComboBox */\n"
"    border-bottom-right-radius: 5px;\n"
"    padding: 1px 1px 1px 1px;\n"
"    image: url(:/resources/dropdown_arrow.png);\n"
"}\n"
"\n"
"QComboBox:drop-down:disabled{\n"
"    border-left-color: #5e7688;\n"
"    padding: 1px 1px 1px 1px;\n"
"    image: url(:/resources/dropdown_arrow_disabled.png);\n"
"}\n"
"\n"
"\n"
"QComboBox QAbstractItemView {\n"
"     border: 1px solid #c5d2d9;\n"
"     border-bottom-left-radius: 5px;\n"
"     border-bottom-right-radius: 5px;\n"
"     selection-background-color:     #4b86b4;\n"
"     outline: solid #2a4d69;\n"
"     font-family: \'Segue UI Emoji\';\n"
"     font-size: 10pt;\n"
"     color: #66767c;\n"
"}\n"
"\n"
"QToolButton{\n"
"    border: 1px solid #c5d2d9;\n"
"    border-radius: 5px;\n"
"    background:     #ffffff;\n"
"}\n"
"\n"
"QToolButton:disabled{\n"
"    background: #acb6ba;\n"
"    border: 1px solid #526c7f;\n"
"    color: #fafbfc;\n"
"}\n"
"\n"
"QScrollArea{\n"
"    border: none;\n"
"}\n"
"\n"
"QScrollBar:vertical{\n"
"    width: 20px;\n"
"    border: none;\n"
"    border-left: 2px solid #e9f0f5;\n"
"    background: #ffffff;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical{\n"
"     background: #baddef;\n"
"     min-height: 0;\n"
"     border:none;\n"
"     border-top, border-bottom: 2px solid #7cbee1;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical{\n"
"     height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical{\n"
"     height: 0px;\n"
"}\n"
"\n"
"\n"
"QScrollBar:horizontal{\n"
"    height: 20px;\n"
"    border: none;\n"
"    border-top: 2px solid #e9f0f5;\n"
"    background: #ffffff;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal{\n"
"     background: #baddef;\n"
"     min-width: 0;\n"
"     border:none;\n"
"     border-left, border-right: 2px solid #7cbee1;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal{\n"
"     width: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal{\n"
"     width: 0px;\n"
"}\n"
"\n"
"QTextBrowser{\n"
"     font-family:\'Segue UI Emoji\';\n"
"     font-size: 10pt;\n"
"     border: 2px solid #e9f0f5;\n"
"     border-radius: 5px;\n"
"     background: #fafbfc;\n"
"}\n"
"\n"
"QPushButton{\n"
"     border:1px solid #4bae54; \n"
"     border-radius:5px; \n"
"     background:#66cc6e; \n"
"     color: #ffffff; \n"
"     padding: 5px 15px 5px 15px; \n"
"     margin: 5px 5px 10px 5px;\n"
"} \n"
"\n"
"QPushButton:disabled{\n"
"     background:#acb6ba; \n"
"     border:1px solid #5e7688;\n"
"     color: #fafbfc;\n"
"} \n"
"QPushButton:hover{\n"
"      background:#6e66cc; \n"
"      border:1px solid #373366;\n"
"}\n"
"\n"
"\n"
"QTableWidget{\n"
"    border:  none;\n"
"    border-radius: 5px;\n"
"    background: #ffffff;\n"
"    outline: none;\n"
"    min-height: 100px;\n"
"    max-height: 120px;\n"
"}\n"
"\n"
"QHeaderView::section{\n"
"    background: #ffffff;\n"
"    border:none;\n"
"    border-bottom: 1px solid #399ee5;\n"
"    font-family:\'Segue UI Emoji\';\n"
"    font-size: 10pt;\n"
"    font-weight： normal;\n"
"    color: #399ee5;\n"
"    padding: 5px 5px 5px 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget::item{\n"
"    border-left, border-bottom: 1px solid #c6d1d6;\n"
"    min-width: 80px;\n"
"    padding: 0 5px 0 0;\n"
"    font-family: \'Segue UI Emoji\';\n"
"    color: #3d5159;\n"
"    font-size: 10pt;\n"
"    min-height: 50px;\n"
"    max-height: 60px;\n"
"    padding: 0 0 0 0;\n"
"}")
        self.mainStackWidget.setObjectName("mainStackWidget")
        self.setting = QtWidgets.QWidget()
        self.setting.setObjectName("setting")
        self.mainSettingLayout = QtWidgets.QVBoxLayout(self.setting)
        self.mainSettingLayout.setContentsMargins(0, 0, 0, 0)
        self.mainSettingLayout.setObjectName("mainSettingLayout")
        self.mainStackWidget.addWidget(self.setting)
        self.log = QtWidgets.QWidget()
        self.log.setObjectName("log")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.log)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 0, 1, 1)
        self.logConsole = QtWidgets.QTextBrowser(self.log)
        font = QtGui.QFont()
        font.setFamily("Segue UI Emoji")
        font.setPointSize(10)
        self.logConsole.setFont(font)
        self.logConsole.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.logConsole.setAutoFillBackground(False)
        self.logConsole.setStyleSheet("")
        self.logConsole.setObjectName("logConsole")
        self.gridLayout_2.addWidget(self.logConsole, 3, 2, 1, 4)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 5, 2, 1, 4)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 4, 2, 1, 4)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem4, 0, 5, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem5, 1, 2, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem6, 1, 4, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem7, 1, 3, 1, 1)
        self.logClear_btn = QtWidgets.QPushButton(self.log)
        self.logClear_btn.setMinimumSize(QtCore.QSize(202, 0))
        self.logClear_btn.setMaximumSize(QtCore.QSize(202, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(10)
        self.logClear_btn.setFont(font)
        self.logClear_btn.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.logClear_btn.setStyleSheet("QPushButton{\n"
"    background: #fa7064;\n"
"    border: 1px solid #f43f2f;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"    background: #f84e41;\n"
"    border: 1px solid #f73728;\n"
"}")
        self.logClear_btn.setObjectName("logClear_btn")
        self.gridLayout_2.addWidget(self.logClear_btn, 1, 5, 1, 1)
        self.mainStackWidget.addWidget(self.log)
        self.table = QtWidgets.QWidget()
        self.table.setObjectName("table")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.table)
        self.gridLayout_5.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_3 = QtWidgets.QLabel(self.table)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout_5.addWidget(self.label_3, 1, 2, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(833, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem8, 5, 2, 1, 2)
        self.tableArea = QtWidgets.QScrollArea(self.table)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        self.tableArea.setFont(font)
        self.tableArea.setStyleSheet("QTextBrowser{\n"
"     background: #f9fafc;\n"
"     font-family: \'Segue UI Emoji\';\n"
"     border: 1px solid #f9fafc;\n"
"     border-radius: 5px;\n"
"     padding: 15px 15px 15px 15px;\n"
"}")
        self.tableArea.setWidgetResizable(True)
        self.tableArea.setObjectName("tableArea")
        self.tableContent = QtWidgets.QWidget()
        self.tableContent.setGeometry(QtCore.QRect(0, 0, 80, 56))
        self.tableContent.setObjectName("tableContent")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tableContent)
        self.gridLayout_3.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tableLayout = QtWidgets.QVBoxLayout()
        self.tableLayout.setContentsMargins(5, 15, 5, 15)
        self.tableLayout.setSpacing(20)
        self.tableLayout.setObjectName("tableLayout")
        self.gridLayout_3.addLayout(self.tableLayout, 2, 1, 1, 1)
        self.tableArea.setWidget(self.tableContent)
        self.gridLayout_5.addWidget(self.tableArea, 4, 2, 1, 2)
        self.line_3 = QtWidgets.QFrame(self.table)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_3.sizePolicy().hasHeightForWidth())
        self.line_3.setSizePolicy(sizePolicy)
        self.line_3.setMaximumSize(QtCore.QSize(16777215, 2))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.line_3.setFont(font)
        self.line_3.setStyleSheet("QWidget{\n"
"     background-color:#399ee5;\n"
"}")
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setLineWidth(-3)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.gridLayout_5.addWidget(self.line_3, 2, 2, 1, 2)
        self.tableExport_btn = QtWidgets.QPushButton(self.table)
        self.tableExport_btn.setMinimumSize(QtCore.QSize(202, 0))
        self.tableExport_btn.setMaximumSize(QtCore.QSize(202, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(10)
        self.tableExport_btn.setFont(font)
        self.tableExport_btn.setObjectName("tableExport_btn")
        self.gridLayout_5.addWidget(self.tableExport_btn, 0, 3, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(833, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem9, 6, 2, 1, 2)
        spacerItem10 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem10, 4, 1, 1, 1)
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem11, 4, 0, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(20, 60, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_5.addItem(spacerItem12, 0, 1, 1, 1)
        self.mainStackWidget.addWidget(self.table)
        self.plot = QtWidgets.QWidget()
        self.plot.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.plot.setObjectName("plot")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.plot)
        self.gridLayout_7.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_7.setObjectName("gridLayout_7")
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem13, 4, 2, 1, 1)
        self.plotExport_btn = QtWidgets.QPushButton(self.plot)
        self.plotExport_btn.setMinimumSize(QtCore.QSize(202, 0))
        self.plotExport_btn.setMaximumSize(QtCore.QSize(202, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(10)
        self.plotExport_btn.setFont(font)
        self.plotExport_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.plotExport_btn.setObjectName("plotExport_btn")
        self.gridLayout_7.addWidget(self.plotExport_btn, 0, 3, 1, 1)
        self.plotArea = QtWidgets.QScrollArea(self.plot)
        self.plotArea.setWidgetResizable(True)
        self.plotArea.setObjectName("plotArea")
        self.plotContent = QtWidgets.QWidget()
        self.plotContent.setGeometry(QtCore.QRect(0, 0, 80, 56))
        self.plotContent.setObjectName("plotContent")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.plotContent)
        self.gridLayout_6.setContentsMargins(0, -1, 0, -1)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.plotViewer = QtWidgets.QGridLayout()
        self.plotViewer.setContentsMargins(15, 15, 15, 15)
        self.plotViewer.setHorizontalSpacing(20)
        self.plotViewer.setVerticalSpacing(15)
        self.plotViewer.setObjectName("plotViewer")
        self.gridLayout_6.addLayout(self.plotViewer, 0, 0, 1, 1)
        self.plotArea.setWidget(self.plotContent)
        self.gridLayout_7.addWidget(self.plotArea, 3, 2, 1, 2)
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem14, 3, 0, 1, 1)
        self.line_4 = QtWidgets.QFrame(self.plot)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_4.sizePolicy().hasHeightForWidth())
        self.line_4.setSizePolicy(sizePolicy)
        self.line_4.setMaximumSize(QtCore.QSize(16777215, 2))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.line_4.setFont(font)
        self.line_4.setStyleSheet("QWidget{\n"
"     background-color:#399ee5;\n"
"}")
        self.line_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_4.setLineWidth(-3)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setObjectName("line_4")
        self.gridLayout_7.addWidget(self.line_4, 2, 2, 1, 2)
        spacerItem15 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem15, 3, 1, 1, 1)
        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem16, 5, 2, 1, 1)
        spacerItem17 = QtWidgets.QSpacerItem(20, 60, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_7.addItem(spacerItem17, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.plot)
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_7.addWidget(self.label_4, 1, 2, 1, 1)
        self.mainStackWidget.addWidget(self.plot)
        self.gridLayout_4.addWidget(self.mainStackWidget, 0, 0, 1, 1)

        self.retranslateUi(MainContentWindow)
        self.mainStackWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainContentWindow)

    def retranslateUi(self, MainContentWindow):
        _translate = QtCore.QCoreApplication.translate
        MainContentWindow.setWindowTitle(_translate("MainContentWindow", "Form"))
        self.logClear_btn.setText(_translate("MainContentWindow", "Clear"))
        self.label_3.setText(_translate("MainContentWindow", "Results"))
        self.tableExport_btn.setText(_translate("MainContentWindow", "Export"))
        self.plotExport_btn.setText(_translate("MainContentWindow", "Export"))
        self.label_4.setText(_translate("MainContentWindow", "Plots"))

