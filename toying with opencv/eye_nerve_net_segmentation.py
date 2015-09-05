from __future__ import division
import sys
import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from common_utils import thinning, toQImage, bgr2qimage
import time
import emoji


class Worker(QThread):

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def processImage(self, image, thresholdValue, offsetValue, channel, alpha=0.5):
        self.image = image
        self.channel = channel
        self.thresholdValue = thresholdValue
        self.offsetValue = offsetValue
        self.alpha = alpha
        self.start()

    def run(self):
        if self.image is None:
            self.emit(SIGNAL("output"), None, None)

        gray = cv2.split(self.image)[self.channel].copy()
        thresh = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, self.thresholdValue, self.offsetValue)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thinned_image = thinning(thresh)
        merged_image = cv2.addWeighted(
            self.image, self.alpha, cv2.cvtColor(thinned_image, cv2.COLOR_GRAY2BGR), 1 - self.alpha, 0)
        pixel_count = thinned_image.shape[0] * thinned_image.shape[1]
        white_pixel_count = np.count_nonzero(thinned_image)
        result_string = "Pixels count / White pixels count = {0}/{1} = {2}".format(
            pixel_count, white_pixel_count, pixel_count / white_pixel_count)
        self.emit(SIGNAL("output"), thinned_image, merged_image, result_string)


class ImageLabel(QLabel):

    def __init__(self, parent=None, acceptDrop=True, windowName='Default windowName'):
        super(ImageLabel, self).__init__(parent)

        self.setMinimumSize(300, 300)
        self.setStyleSheet("border: 1px solid black;")
        self.setAcceptDrops(acceptDrop)
        self.image = None
        self.qimage = None
        self.channel = None
        self.windowName = windowName

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

        # Channel of interest = the one with max sum value
        self.channel = np.argmax(
            np.array([np.sum(x) for x in cv2.split(self.image)]))

    def resizeEvent(self, e):
        if self.image is None:
            return

        self.setScaledPixmap()

    def setScaledPixmap(self):
        scaledPixmap = QPixmap.fromImage(self.qimage).scaled(
            self.size(), Qt.KeepAspectRatio)
        self.setPixmap(scaledPixmap)

    def mouseDoubleClickEvent(self, event):
        self.popUpImageView()

    def popUpImageView(self):
        if self.image is None:
            return

        popUpImage = cv2.resize(self.image, dsize=None, fx=0.75, fy=0.75)
        cv2.imshow(self.windowName, popUpImage)


class SegmentationWidget(QWidget):

    def __init__(self, parent=None):
        super(SegmentationWidget, self).__init__(parent)

        self.gray = None
        self.thread = Worker()

        self.setupUI()
        self.setupEvents()

    def setupUI(self):
        self.setWindowTitle(emoji.emojize(':cloud::snowflake:'))
        self.inputImageLabel = ImageLabel(windowName='Input')
        self.skeletonImageLabel = ImageLabel(
            acceptDrop=False, windowName='Skeletonized')
        self.mergedImageLabel = ImageLabel(
            acceptDrop=False, windowName='Merged')

        self.thresholdBlockLabel = QLabel('ThresholdBlock value: 39')
        self.thresholdBlockSlider = QSlider(Qt.Horizontal, self)
        self.thresholdBlockSlider.setRange(1, 199)
        self.thresholdBlockSlider.setValue(39)
        self.thresholdBlockSlider.setSingleStep(2)
        self.thresholdBlockSlider.setFocusPolicy(Qt.TabFocus)
        self.thresholdBlockSlider.setFocus()

        self.offsetLabel = QLabel('Offset value: 10')
        self.offsetSlider = QSlider(Qt.Horizontal, self)
        self.offsetSlider.setRange(0, 100)
        self.offsetSlider.setValue(10)
        self.offsetSlider.setFocusPolicy(Qt.TabFocus)

        self.resultLabel = QLabel('Result displayed here.')

        self.alphaSliderLabel = QLabel('Alpha (blending factor): 0.5')
        self.alphaSlider = QSlider(Qt.Horizontal, self)
        self.alphaSlider.setRange(0, 100)
        self.alphaSlider.setValue(50)
        self.alphaSlider.setFocusPolicy(Qt.TabFocus)

        sublayout = QGridLayout()
        sublayout.addWidget(self.thresholdBlockLabel, 0, 0, 1, 2)
        sublayout.addWidget(self.thresholdBlockSlider, 1, 0, 1, 2)
        sublayout.addWidget(self.offsetLabel, 2, 0, 1, 2)
        sublayout.addWidget(self.offsetSlider, 3, 0, 1, 2)
        sublayout.addWidget(self.alphaSliderLabel, 4, 0, 1, 2)
        sublayout.addWidget(self.alphaSlider, 5, 0, 1, 2)
        sublayout.addWidget(self.resultLabel, 6, 0, 1, 2)
        sublayout.setRowStretch(0, 0)
        sublayout.setRowStretch(1, 0)
        sublayout.setRowStretch(2, 0)
        sublayout.setRowStretch(3, 0)
        sublayout.setRowStretch(4, 0)
        sublayout.setRowStretch(5, 0)
        sublayout.setRowStretch(6, 0)

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
        # Heavy processing related events
        self.thresholdBlockSlider.valueChanged[
            int].connect(self.prepareUpdateUI)
        self.offsetSlider.valueChanged[int].connect(self.prepareUpdateUI)
        self.connect(
            self.thread, SIGNAL("output"), self.updateImage)
        self.thread.terminated.connect(self.updateUI)
        self.thread.finished.connect(self.updateUI)

        # Light processing related events
        self.alphaSlider.valueChanged[int].connect(self.updateMergedImage)

    def prepareUpdateUI(self):
        self.offsetLabel.setText(
            "Offset value: {0}".format(self.offsetSlider.value()))
        self.thresholdBlockLabel.setText(
            "Threshold block value: {0}".format(self.thresholdBlockSlider.value()))
        self.alphaSliderLabel.setText("Alpha value: {0}".format(self.alphaSlider.value() / 100))

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
        self.thread.processImage(self.inputImageLabel.image, self.thresholdBlockSlider.value(
        ), self.offsetSlider.value(), self.inputImageLabel.channel, alpha=self.alphaSlider.value() / 100)

    def updateUI(self):
        self.thresholdBlockSlider.setEnabled(True)
        self.offsetSlider.setEnabled(True)

    def updateImage(self, thinned_image, merged_image, result_string):
        if thinned_image is None or merged_image is None:
            return

        self.skeletonImageLabel.image = thinned_image
        self.skeletonImageLabel.qimage = toQImage(thinned_image)
        self.skeletonImageLabel.setScaledPixmap()

        self.mergedImageLabel.image = merged_image
        self.mergedImageLabel.qimage = bgr2qimage(merged_image)
        self.mergedImageLabel.setScaledPixmap()
        self.mergedImageLabel.popUpImageView()

        self.resultLabel.setText(result_string)

    def updateMergedImage(self):
        alpha = self.alphaSlider.value() / 100
        self.alphaSliderLabel.setText("Alpha value: {0}".format(alpha))

        if self.inputImageLabel.image is None or self.skeletonImageLabel.image is None:
            return

        merged_image = cv2.addWeighted(self.inputImageLabel.image, alpha, cv2.cvtColor(
            self.skeletonImageLabel.image, cv2.COLOR_GRAY2BGR), 1.0 - alpha, 0)
        self.mergedImageLabel.image = merged_image
        self.mergedImageLabel.qimage = bgr2qimage(merged_image)
        self.mergedImageLabel.setScaledPixmap()
        self.mergedImageLabel.popUpImageView()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    segWidget = SegmentationWidget()
    segWidget.show()
    app.exec_()
