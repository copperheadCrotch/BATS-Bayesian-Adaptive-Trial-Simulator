# Import PyQt
from PyQt5 import QtGui, QtCore, QtWidgets, Qt


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
        
        