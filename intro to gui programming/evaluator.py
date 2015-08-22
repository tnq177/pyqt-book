from __future__ import division
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.browser = QTextBrowser()

        self.lineEdit = QLineEdit('Type any expression and press Enter')
        self.lineEdit.selectAll()

        # Although we did not specify the parent of lineEdit or browser
        # Since we add them into layout, and set it to be the layout of our form
        # Form is now automatically parent of layout and all the widgets
        # When parent is deleted, all its children will be deleted too.
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)

        self.lineEdit.setFocus()
        self.lineEdit.returnPressed.connect(self.updateUI) # <3 this new syntax
        self.setWindowTitle('Evaluator')

    def updateUI(self):
        try:
            text = unicode(self.lineEdit.text())
            self.browser.append("%s = <b>%s</b>" % (text, eval(text)))
        except Exception, e:
            self.browser.append("<font color=red>%s is invalid!</font>" % text)

        self.lineEdit.setText('')

app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()