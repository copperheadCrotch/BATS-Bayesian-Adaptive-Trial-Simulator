# Import PyQt
from PyQt5 import QtGui, QtCore, QtWidgets, Qt


# Event filter class
# Disable scroll on comboBox
class WheelFilter(QtCore.QObject):
    
    def eventFilter(self, source, event):
        
        # Filter out the wheel event
        if event.type() == QtCore.QEvent.Wheel:
             
            return True
    
        return False



# Emit signal from focus out event
class FocusOutFilter(QtCore.QObject):
    
    # Create a focus out signal
    focusOut = QtCore.pyqtSignal(QtCore.QObject)
    def eventFilter(self, widget, event):
        
        # If the event is focus out, emit the signal for checking input
        if event.type() == QtCore.QEvent.FocusOut:

            # Emit the event
            self.focusOut.emit(widget)
            self.sendin = widget
    
        # Do not filter the event
        return False
    


# Emit signal from focus out event
class TableFocusOutFilter(QtCore.QObject):
    
    # Create a focus out signal
    tableFocusOut = QtCore.pyqtSignal(QtCore.QObject)
    def eventFilter(self, widget, event):
        
        # If the event is focus out, emit the signal for checking input
        if event.type() == QtCore.QEvent.FocusOut:

            # Emit the event
            self.tableFocusOut.emit(widget)
            self.sendin = widget

        # Do not filter the event
        return False
    
    
# Emit signal from hover out event
class HoverLeaveDocFilter(QtCore.QObject):
    
    # Create a hover out signal
    hoverEnterDoc = QtCore.pyqtSignal(QtCore.QObject)
    hoverLeaveDoc = QtCore.pyqtSignal(QtCore.QObject)
    docinFocus = False
    def eventFilter(self, widget, event):
        
        # If the event is focus out, emit the signal for clear doc
        if event.type() == QtCore.QEvent.FocusOut:
            
            # Emit the event
            self.hoverLeaveDoc.emit(widget)
            self.docinFocus = False
            
        # If it is a focus in event, focus on the widget
        if event.type() == QtCore.QEvent.FocusIn:
            
            self.hoverEnterDoc.emit(widget)
            self.docinFocus = True
                                
        # If the event is hover enter, emit the signal for label
        if event.type() == QtCore.QEvent.HoverEnter and not self.docinFocus:
            
            self.hoverEnterDoc.emit(widget)
        
        if event.type() == QtCore.QEvent.HoverLeave and not self.docinFocus:
            
            self.hoverLeaveDoc.emit(widget)
            
    
        return False
    





