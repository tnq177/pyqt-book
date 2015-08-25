'''
From https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots
This reminds me of an programming exercise in my first year.
We were asked to write a program which drew a wavelength or something in real
time and user could choose to change the parameters of the function.
'''

import math
import random
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Worker(QThread):

    def __init__(self, parent=None):

        QThread.__init__(self, parent)
        self.exiting = False
        self.size = QSize(0, 0)
        self.stars = 0

        self.path = QPainterPath()
        angle = 2 * math.pi / 5
        self.outerRadius = 20
        self.innerRadius = 8
        self.path.moveTo(self.outerRadius, 0)
        for step in range(1, 6):
            self.path.lineTo(
                self.innerRadius * math.cos((step - 0.5) * angle),
                self.innerRadius * math.sin((step - 0.5) * angle)
            )
            self.path.lineTo(
                self.outerRadius * math.cos(step * angle),
                self.outerRadius * math.sin(step * angle)
            )
        self.path.closeSubpath()

    def __del__(self):
        self.exiting = True
        self.wait()

    def render(self, size, stars):
        self.size = size
        self.stars = stars
        self.start()

    def run(self):

        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.

        random.seed()
        n = self.stars
        width = self.size.width()
        height = self.size.height()

        while not self.exiting and n > 0:

            image = QImage(self.outerRadius * 2, self.outerRadius * 2,
                           QImage.Format_ARGB32)
            image.fill(qRgba(0, 0, 0, 0))

            x = random.randrange(0, width)
            y = random.randrange(0, height)
            angle = random.randrange(0, 360)
            red = random.randrange(0, 256)
            green = random.randrange(0, 256)
            blue = random.randrange(0, 256)
            alpha = random.randrange(0, 256)

            painter = QPainter()
            painter.begin(image)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(red, green, blue, alpha))
            painter.translate(self.outerRadius, self.outerRadius)
            painter.rotate(angle)
            painter.drawPath(self.path)
            painter.end()

            self.emit(SIGNAL("output(QRect, QImage)"),
                      QRect(x - self.outerRadius, y - self.outerRadius,
                            self.outerRadius * 2, self.outerRadius * 2), image)
            n -= 1


class Window(QWidget):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.thread = Worker()
        self.setupUI()

    def setupUI(self):
        label = QLabel(self.tr('Number of stars:'))
        self.spinbox = QSpinBox()
        self.spinbox.setMaximum(10000)
        self.spinbox.setValue(100)
        self.startButton = QPushButton(self.tr('&Start'))
        self.viewer = QLabel()
        self.viewer.setFixedSize(300, 300)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.spinbox, 0, 1)
        layout.addWidget(self.startButton, 0, 2)
        layout.addWidget(self.viewer, 1, 0, 1, 3)
        self.setLayout(layout)

        self.setWindowTitle(self.tr('Simple threading example'))

        self.setupEvents()

    def setupEvents(self):
        self.thread.finished.connect(self.updateUI)
        self.thread.terminated.connect(self.updateUI)
        # self.thread.output[QRect, QImage].connect(self.addImage)
        self.connect(self.thread, SIGNAL("output(QRect, QImage)"), self.addImage)
        self.startButton.clicked.connect(self.makePicture)

    def makePicture(self):
        self.spinbox.setReadOnly(True)
        self.startButton.setEnabled(False)
        pixmap = QPixmap(self.viewer.size())
        pixmap.fill(Qt.black)
        self.viewer.setPixmap(pixmap)
        self.thread.render(self.viewer.size(), self.spinbox.value())

    def addImage(self, rect, image):
        pixmap = self.viewer.pixmap()
        painter = QPainter()
        painter.begin(pixmap)
        painter.drawImage(rect, image)
        painter.end()
        self.viewer.update(rect)

    def updateUI(self):
        self.spinbox.setReadOnly(False)
        self.startButton.setEnabled(True)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
