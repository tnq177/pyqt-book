from __future__ import division
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import emoji


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.setupGUI()

    def setupGUI(self):
        self.setWindowTitle('Just an awesome interest calculator')

        principalLabel = QLabel('Principal:')
        self.principal = QDoubleSpinBox()
        self.principal.setRange(0.0, 1000000)
        self.principal.setValue(0.0)
        self.principal.setPrefix('$ ')

        rateLabel = QLabel('Rate:')
        self.rate = QDoubleSpinBox()
        self.rate.setRange(0.0, 1000000)
        self.rate.setValue(0.0)
        self.rate.setSuffix(' %')

        yearsLabel = QLabel('Years:')
        self.years = QSpinBox()
        self.years.setSuffix(' years')

        amountLabel = QLabel('Amount')
        self.amount = QLabel('0')

        smiley = QLabel(emoji.emojize(':cloud::snowflake:'))
        smiley.setFont(QFont('Arial', 30))

        layout = QGridLayout()
        layout.addWidget(principalLabel, 0, 0)
        layout.addWidget(self.principal, 0, 1)
        layout.addWidget(rateLabel, 1, 0)
        layout.addWidget(self.rate, 1, 1)
        layout.addWidget(yearsLabel, 2, 0)
        layout.addWidget(self.years, 2, 1)
        layout.addWidget(amountLabel, 3, 0)
        layout.addWidget(self.amount, 3, 1)
        # Add an emoji, just to be awesome
        layout.addWidget(smiley, 4, 0)

        self.setLayout(layout)

        self.setupSignalsAndSlots()

    def setupSignalsAndSlots(self):
        self.principal.valueChanged['double'].connect(self.updateUI)
        self.rate.valueChanged['double'].connect(self.updateUI)
        self.years.valueChanged.connect(self.updateUI)

    def updateUI(self):
        principalValue = self.principal.value()
        rateValue = self.rate.value()
        yearsValue = self.years.value()

        amountValue = principalValue * ((1 + (rateValue / 100.0)) ** yearsValue)
        self.amount.setText("{0}".format(amountValue))


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()