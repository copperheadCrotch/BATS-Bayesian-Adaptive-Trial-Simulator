# Import PyQt
from PyQt5 import QtGui, QtCore, QtWidgets, Qt


# Validator for futile, effifcacy and clinical significant difference
class StrictDoubleValidator(QtGui.QDoubleValidator):

    def __init__(self, parent = None):

        QtGui.QDoubleValidator.__init__(self, parent)
        self.setNotation(QtGui.QDoubleValidator.StandardNotation)


    def validate(self, input, pos):

        state, input, pos = QtGui.QDoubleValidator.validate(self, input, pos)
        if state == QtGui.QValidator.Invalid:
            
            QtWidgets.QApplication.beep()
            return (QtGui.QValidator.Invalid, input, pos)
        
        elif state == QtGui.QValidator.Intermediate:
            
            return (QtGui.QValidator.Intermediate, input, pos)
        
        if pos == 1:
        
            try: 
                
                if float(str(input)) > 1:
                    
                    QtWidgets.QApplication.beep()
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                QtWidgets.QApplication.beep()
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos == 2:
            
            if not str(input)[pos-1] == ".":
                
                QtWidgets.QApplication.beep() 
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos > 2:
        
            try:
                
                if  float(str(input)) > 1:
                    
                    QtWidgets.QApplication.beep() 
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                QtWidgets.QApplication.beep()
                return (QtGui.QValidator.Invalid, input, pos)
        
        return (QtGui.QValidator.Acceptable, input, pos)
        
        

# Validator for integers
class StrictIntValidator(QtGui.QIntValidator):
    
    
    def __init__(self, parent = None):
        
        QtGui.QIntValidator.__init__(self, parent)
    
    def validate(self, input, pos):
               
        state, input, pos = QtGui.QIntValidator.validate(self, input, pos)
        if state == QtGui.QValidator.Invalid:
            
            QtWidgets.QApplication.beep()
            return (QtGui.QValidator.Invalid, input, pos)
        
        elif state == QtGui.QValidator.Intermediate:
            
            return(QtGui.QValidator.Intermediate, input, pos)
        
        return (QtGui.QValidator.Acceptable, input, pos)

        
        
# Validator for allocation ratio
class ContinuousValidator(QtGui.QDoubleValidator):

    def __init__(self, parent = None):

        QtGui.QDoubleValidator.__init__(self, parent)
        self.setNotation(QtGui.QDoubleValidator.StandardNotation)

    def validate(self, input, pos):

        state, input, pos = QtGui.QDoubleValidator.validate(self, input, pos)
        if state == QtGui.QValidator.Invalid:
        
            QtWidgets.QApplication.beep()
            return (QtGui.QValidator.Invalid, input, pos)

        elif state == QtGui.QValidator.Intermediate:
            
            return (QtGui.QValidator.Intermediate, input, pos)
                
        if pos == 1:
        
            try: 
                
                if float(str(input)) > 4:
                    
                    QtWidgets.QApplication.beep() 
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                QtWidgets.QApplication.beep() 
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos == 2:
        
            if not str(input)[pos-1] == ".":
                
                QtWidgets.QApplication.beep() 
                return (QtGui.QValidator.Invalid, input, pos)
        
        elif pos > 2:
            
            try:
                
                if  float(str(input)) >= 4:
                    
                    QtWidgets.QApplication.beep()  
                    return (QtGui.QValidator.Invalid, input, pos)
            
            except:
                
                QtWidgets.QApplication.beep()    
                return (QtGui.QValidator.Invalid, input, pos)
        
        return (QtGui.QValidator.Acceptable, input, pos)
    
    
            
# Validator for table entry, rewrite the table
class TableDoubleValidator(QtWidgets.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtWidgets.QLineEdit(widget)
        self.cell_validator = StrictDoubleValidator()
        self.cell_validator.setRange(0.0, 1.0, 3)
        self.cellEditor.setValidator(self.cell_validator)

        return self.cellEditor



# Validator for patients assignments
# Will be used in version 1 and version 2
class TableIntValidator(QtWidgets.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtWidgets.QLineEdit(widget)
        self.cell_validator = StrictIntValidator(self)
        self.cell_validator.setRange(2, 2000)
        self.cellEditor.setValidator(self.cell_validator)
        
        return self.cellEditor



# Validator for prior information
class TablePriorIntValidator(QtWidgets.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtWidgets.QLineEdit(widget)
        self.cell_validator = StrictIntValidator(self)
        self.cell_validator.setRange(1, 5000)
        self.cellEditor.setValidator(self.cell_validator)
        
        return self.cellEditor
        
        

# Validator for predictive probability
class TablePredIntValidator(QtWidgets.QStyledItemDelegate):

    def createEditor(self, widget, option, index):

        self.cellEditor = QtWidgets.QLineEdit(widget)
        self.cell_validator = StrictIntValidator(self)
        self.cell_validator.setRange(0, 5000)
        self.cellEditor.setValidator(self.cell_validator)
        
        return self.cellEditor
    
    
    
    