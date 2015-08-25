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

        self.setLayout(layout)


app = QApplication(sys.argv)
example = Example()
example.show()
app.exec_()
