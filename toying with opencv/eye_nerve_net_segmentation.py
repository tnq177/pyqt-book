import sys
import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from common_utils import thinning, toQImage, bgr2qimage

class ImageLabel(QLabel):

    def __init__(self, parent=None, acceptDrop=True):
        super(ImageLabel, self).__init__(parent)

        self.setMinimumSize(300, 300)
        self.setStyleSheet("border: 1px solid black;")
        self.setAcceptDrops(acceptDrop)
        self.image = None
        self.qimage = None

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        image_url = e.mimeData().urls()[0].toLocalFile()
        self.image = cv2.imread(str(image_url))
        self.qimage = bgr2qimage(self.image)
        self.setScaledPixmap()

    def resizeEvent(self, e):
        if self.image is None:
            return

        self.setScaledPixmap()

    def setScaledPixmap(self):
        scaledPixmap = QPixmap.fromImage(self.qimage).scaled(
            self.size(), Qt.KeepAspectRatio)
        self.setPixmap(scaledPixmap)


class SegmentationWidget(QWidget):

    def __init__(self, parent=None):
        super(SegmentationWidget, self).__init__(parent)

        self.gray = None
        self.setupUI()
        self.setupEvents()

    def setupUI(self):
        self.inputImageLabel = ImageLabel()
        self.skeletonImageLabel = ImageLabel(acceptDrop=False)
        self.mergedImageLabel = ImageLabel(acceptDrop=False)

        self.thresholdBlockLabel = QLabel('ThresholdBlock value: 39')
        self.thresholdBlockSlider = QSlider(Qt.Horizontal, self)
        self.thresholdBlockSlider.setRange(1, 199)
        self.thresholdBlockSlider.setFocusPolicy(Qt.NoFocus)
        self.thresholdBlockSlider.setValue(39)
        self.thresholdBlockSlider.setSingleStep(2)

        self.offsetLabel = QLabel('Offset value: 10')
        self.offsetSlider = QSlider(Qt.Horizontal, self)
        self.offsetSlider.setRange(0, 100)
        self.offsetSlider.setFocusPolicy(Qt.NoFocus)
        self.offsetSlider.setValue(10)

        sublayout = QGridLayout()
        sublayout.addWidget(self.thresholdBlockLabel, 0, 0, 1, 2)
        sublayout.addWidget(self.thresholdBlockSlider, 1, 0, 1, 2)
        sublayout.addWidget(self.offsetLabel, 2, 0, 1, 2)
        sublayout.addWidget(self.offsetSlider, 3, 0, 1, 2)
        sublayout.setRowStretch(0, 0)
        sublayout.setRowStretch(1, 0)
        sublayout.setRowStretch(2, 0)
        sublayout.setRowStretch(3, 0)

        layout = QGridLayout()
        layout.addWidget(self.inputImageLabel, 0, 0)
        layout.addWidget(self.skeletonImageLabel, 0, 1)
        layout.addWidget(self.mergedImageLabel, 1, 0)
        layout.addLayout(sublayout, 1, 1)

        # Make cells have the same height/width
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)

        self.setLayout(layout)

    def setupEvents(self):
        self.thresholdBlockSlider.valueChanged[int].connect(self.updateUI)
        self.offsetSlider.valueChanged[int].connect(self.updateUI)

    def updateUI(self):
        newThresholdBlockValue = self.thresholdBlockSlider.value()
        if newThresholdBlockValue % 2 == 0:
            if newThresholdBlockValue == 100:
                newThresholdBlockValue = 99
            else:
                newThresholdBlockValue += 1
            self.thresholdBlockSlider.setValue(newThresholdBlockValue)

        self.offsetLabel.setText(
            "Offset value: {0}".format(self.offsetSlider.value()))
        self.thresholdBlockLabel.setText(
            "Threshold block value: {0}".format(self.thresholdBlockSlider.value()))

        if self.inputImageLabel.image is None:
            return

        self.gray = cv2.cvtColor(
            self.inputImageLabel.image, cv2.COLOR_BGR2GRAY)
        self.thresh = cv2.adaptiveThreshold(~self.gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, self.thresholdBlockSlider.value(), self.offsetSlider.value())

        # self.skeletonImageLabel.image = img_as_ubyte(skeletonize(self.thresh))
        self.skeletonImageLabel.image = thinning(self.thresh)
        self.skeletonImageLabel.qimage = toQImage(
            self.skeletonImageLabel.image)
        self.skeletonImageLabel.setScaledPixmap()

        self.mergedImageLabel.image = self.thresh
        self.mergedImageLabel.qimage = toQImage(self.mergedImageLabel.image)
        self.mergedImageLabel.setScaledPixmap()


app = QApplication(sys.argv)
segWidget = SegmentationWidget()
segWidget.show()
app.exec_()
