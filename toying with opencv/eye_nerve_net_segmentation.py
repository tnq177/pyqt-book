import sys
import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from common_utils import thinning, toQImage, bgr2qimage


class Worker(QThread):

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def processImage(self, image, thresholdValue, offsetValue):
        self.image = image
        self.thresholdValue = thresholdValue
        self.offsetValue = offsetValue
        self.start()

    def run(self):
        if self.image is None:
            self.emit(SIGNAL("output"), None, None)

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, self.thresholdValue, self.offsetValue)
        thinned_image = thinning(thresh)
        self.emit(SIGNAL("output"), thinned_image, thresh)


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
        self.thread = Worker()

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
        self.thresholdBlockSlider.valueChanged[
            int].connect(self.prepareUpdateUI)
        self.offsetSlider.valueChanged[int].connect(self.prepareUpdateUI)
        self.connect(
            self.thread, SIGNAL("output"), self.updateImage)
        self.thread.terminated.connect(self.updateUI)
        self.thread.finished.connect(self.updateUI)

    def prepareUpdateUI(self):
        if self.inputImageLabel.image is None:
            return

        newThresholdBlockValue = self.thresholdBlockSlider.value()
        if newThresholdBlockValue % 2 == 0:
            if newThresholdBlockValue == 100:
                newThresholdBlockValue = 99
            else:
                newThresholdBlockValue += 1
            self.thresholdBlockSlider.setValue(newThresholdBlockValue)

        self.thresholdBlockSlider.setEnabled(False)
        self.offsetSlider.setEnabled(False)
        self.thread.processImage(
            self.inputImageLabel.image, self.thresholdBlockSlider.value(), self.offsetSlider.value())

    def updateUI(self):
        self.thresholdBlockSlider.setEnabled(True)
        self.offsetSlider.setEnabled(True)

    def updateImage(self, thinned_image, merged_image):
        self.offsetLabel.setText(
            "Offset value: {0}".format(self.offsetSlider.value()))
        self.thresholdBlockLabel.setText(
            "Threshold block value: {0}".format(self.thresholdBlockSlider.value()))

        if thinned_image is None or merged_image is None:
            return

        self.skeletonImageLabel.image = thinned_image
        self.skeletonImageLabel.qimage = toQImage(thinned_image)
        self.skeletonImageLabel.setScaledPixmap()

        self.mergedImageLabel.image = merged_image
        self.mergedImageLabel.qimage = toQImage(merged_image)
        self.mergedImageLabel.setScaledPixmap()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    segWidget = SegmentationWidget()
    segWidget.show()
    app.exec_()
