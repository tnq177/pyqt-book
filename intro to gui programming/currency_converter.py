from __future__ import division
import sys
import urllib2
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        date = self.getData()
        rates = sorted(self.rates.keys())
        dateLabel = QLabel(date)

        self.fromComboBox = QComboBox()
        self.fromComboBox.addItems(rates)
        self.fromSpinBox = QDoubleSpinBox()
        self.fromSpinBox.setRange(0.01, 10000000.0)
        self.fromSpinBox.setValue(1.00)
        self.toComboBox = QComboBox()
        self.toComboBox.addItems(rates)
        self.toLabel = QLabel("1.00")

        grid = QGridLayout()
        grid.addWidget(dateLabel, 0, 0)
        grid.addWidget(self.fromComboBox, 1, 0)
        grid.addWidget(self.fromSpinBox, 1, 1)
        grid.addWidget(self.toComboBox, 2, 0)
        grid.addWidget(self.toLabel, 2, 1)
        self.setLayout(grid)

        # In evaluator.py, we have seen the new PyQT4 signal & slot syntax
        # which is more Python-like than the old QT style.
        # Below is how to use the new syntax when the event receives different
        # types of params. E.g., currentIndexChanged can take either int or QString
        self.fromComboBox.currentIndexChanged['int'].connect(self.updateUI)
        self.toComboBox.currentIndexChanged['int'].connect(self.updateUI)
        self.fromSpinBox.valueChanged['double'].connect(self.updateUI)
        self.setWindowTitle('Currency converter')

    def updateUI(self):
        to_ = unicode(self.toComboBox.currentText())
        from_ = unicode(self.fromComboBox.currentText())
        amount = (self.rates[from_] / self.rates[to_]) * \
            self.fromSpinBox.value()
        self.toLabel.setText("{0}".format(amount))

    def getData(self):
        self.rates = {}

        try:
            date = 'Unknown'
            fh = urllib2.urlopen(
                'http://www.bankofcanada.ca/en/markets/csv/exchange_eng.csv')

            for line in fh:
                if not line or line.startswith('#') or line.startswith('Closing'):
                    continue

                fields = line.split(', ')
                if line.startswith('Date '):
                    date = fields[-1]
                else:
                    try:
                        value = float(fields[-1])
                        self.rates[unicode(fields[0])] = value
                    except ValueError:
                        pass

            return "Exchange rate Date: {0}".format(date)
        except Exception, e:
            raise "Failed to download: \n{0}".format(e)


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
