import sys
import cv2
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2qimage import toQImage
from scipy import weave

# Credit: https://github.com/bsdnoobz/zhang-suen-thinning/blob/master/


def _thinningIteration(im, iter):
    I, M = im, np.zeros(im.shape, np.uint8)
    expr = """
    for (int i = 1; i < NI[0]-1; i++) {
        for (int j = 1; j < NI[1]-1; j++) {
            int p2 = I2(i-1, j);
            int p3 = I2(i-1, j+1);
            int p4 = I2(i, j+1);
            int p5 = I2(i+1, j+1);
            int p6 = I2(i+1, j);
            int p7 = I2(i+1, j-1);
            int p8 = I2(i, j-1);
            int p9 = I2(i-1, j-1);
            int A  = (p2 == 0 && p3 == 1) + (p3 == 0 && p4 == 1) +
                     (p4 == 0 && p5 == 1) + (p5 == 0 && p6 == 1) +
                     (p6 == 0 && p7 == 1) + (p7 == 0 && p8 == 1) +
                     (p8 == 0 && p9 == 1) + (p9 == 0 && p2 == 1);
            int B  = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
            int m1 = iter == 0 ? (p2 * p4 * p6) : (p2 * p4 * p8);
            int m2 = iter == 0 ? (p4 * p6 * p8) : (p2 * p6 * p8);
            if (A == 1 && B >= 2 && B <= 6 && m1 == 0 && m2 == 0) {
                M2(i,j) = 1;
            }
        }
    }
    """

    weave.inline(expr, ["I", "iter", "M"])
    return (I & ~M)


def thinning(src):
    dst = src.copy() / 255
    prev = np.zeros(src.shape[:2], np.uint8)
    diff = None

    while True:
        dst = _thinningIteration(dst, 0)
        dst = _thinningIteration(dst, 1)
        diff = np.absolute(dst - prev)
        prev = dst.copy()
        if np.sum(diff) == 0:
            break

    return dst * 255


def bgr2qimage(img):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return toQImage(rgb)


class ImageLabel(QLabel):

    def __init__(self, parent=None, acceptDrop=True):
        super(ImageLabel, self).__init__(parent)

        self.setMinimumSize(300, 300)
        self.setStyleSheet("border: 1px solid black;")
        self.setAcceptDrops(acceptDrop)
        self.image = None
        self.qimage = None
        self.hasImage = False

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        image_url = e.mimeData().urls()[0].toLocalFile()
        self.image = cv2.imread(str(image_url))
        self.qimage = bgr2qimage(self.image)
        self.setPixmap(QPixmap.fromImage(self.qimage))
        self.hasImage = True

    def resizeEvent(self, e):
        if not self.hasImage:
            return

        scaledPixmap = QPixmap.fromImage(self.qimage).scaled(self.size(), Qt.KeepAspectRatio)
        self.setPixmap(scaledPixmap)


class SegmentationWidget(QWidget):

    def __init__(self, parent=None):
        super(SegmentationWidget, self).__init__(parent)

        self.gray = None
        self.setupUI()

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

        self.setupEvents()

    def setupEvents(self):
        self.thresholdBlockSlider.valueChanged[int].connect(self.updateUI)
        self.offsetSlider.valueChanged[int].connect(self.updateUI)

    def updateUI(self):
        if not self.inputImageLabel.hasImage:
            return

        self.offsetLabel.setText(
            "Offset value: {0}".format(self.offsetSlider.value()))
        self.thresholdBlockLabel.setText(
            "Threshold block value: {0}".format(self.thresholdBlockSlider.value()))
        self.gray = cv2.cvtColor(
            self.inputImageLabel.image, cv2.COLOR_BGR2GRAY)
        # self.thresh = ~threshold_adaptive(~self.gray, self.thresholdBlockSlider.value(), self.offsetSlider.value())
        self.thresh = cv2.adaptiveThreshold(~self.gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, self.thresholdBlockSlider.value(), self.offsetSlider.value())

        # self.skeletonImageLabel.image = img_as_ubyte(skeletonize(self.thresh))
        self.skeletonImageLabel.image = thinning(self.thresh)
        self.skeletonImageLabel.qimage = toQImage(
            self.skeletonImageLabel.image)
        self.skeletonImageLabel.setPixmap(
            QPixmap.fromImage(self.skeletonImageLabel.qimage))
        self.skeletonImageLabel.hasImage = True

        self.mergedImageLabel.image = self.thresh
        self.mergedImageLabel.qimage = toQImage(self.mergedImageLabel.image)
        self.mergedImageLabel.setPixmap(
            QPixmap.fromImage(self.mergedImageLabel.qimage))
        self.mergedImageLabel.hasImage = True


app = QApplication(sys.argv)
segWidget = SegmentationWidget()
segWidget.show()
app.exec_()
