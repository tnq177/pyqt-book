import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ImageLabel(QLabel):

    def __init__(self, parent=None, acceptDrop=True):
        super(ImageLabel, self).__init__(parent)

        self.setMinimumSize(100, 100)
        self.setStyleSheet("border: 5px solid black;")
        self.setAcceptDrops(acceptDrop)
        self.pixmap = QPixmap('./data/angular_momentum.jpg')

    def resizeEvent(self, event):
        # One can also scaled with fixed width/height, and still keep
        # the aspect ratio. See the docs:
        # http://pyqt.sourceforge.net/Docs/PyQt4/qpixmap.html#scaled-2
        scaledPixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio)
        self.setPixmap(scaledPixmap)


class Example(QWidget):

    def __init__(self, parent=None):
        super(Example, self).__init__(parent)

        self.setupUI()

    def setupUI(self):
        layout = QGridLayout()

        imageLabel1 = ImageLabel()
        imageLabel2 = ImageLabel()
        imageLabel3 = ImageLabel()
        imageLabel4 = ImageLabel()

        layout.addWidget(imageLabel1, 0, 0)
        layout.addWidget(imageLabel2, 0, 1)
        layout.addWidget(imageLabel3, 1, 0)
        layout.addWidget(imageLabel4, 1, 1)

        # Make four cells have the same width/height
        # The 1000 term is just a stretch factor
        # See http://doc.qt.io/qt-4.8/layout.html#stretch-factors
        # It's relative, so 1000 or 1 are just the same
        # layout.setColumnStretch(0, 1000)
        # layout.setColumnStretch(1, 1000)
        # layout.setColumnStretch(2, 1000)
        # layout.setColumnStretch(3, 1000)
        # layout.setRowStretch(0, 1000)
        # layout.setRowStretch(1, 1000)
        # layout.setRowStretch(2, 1000)
        # layout.setRowStretch(3, 1000)

        # However, it seems like a positive stretch factor
        # impedes the cell from expanding
        # Setting them all to 0 make the widget expand full of the cells
        # Hmm.. Learning about expanding policy later
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)
        layout.setColumnStretch(3, 0)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setRowStretch(3, 0)
        
        self.setLayout(layout)


app = QApplication(sys.argv)
example = Example()
example.show()
app.exec_()
