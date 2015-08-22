import sys
import cv2
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rgb2qimage import toQImage

def bgr2qimage(img):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return toQImage(rgb)

def customSetPixmap(label, image):
    pixmap = QPixmap().fromImage(image)
    pixmap = pixmap.scaledToHeight(label.height())

    label.setPixmap(pixmap)


class ImageLabel(QLabel):

    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)

        self.setFixedSize(600, 800)
        self.setStyleSheet("border: 5px solid black; padding: None;")
        self.setAcceptDrops(True)
        self.image = None

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        image_url = e.mimeData().urls()[0].toLocalFile()
        self.image = cv2.imread(str(image_url))
        qimage = bgr2qimage(self.image)
        customSetPixmap(self, qimage)


class ContourViewer(QWidget):

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('Toying with PyQt4 and OpenCV Contour')
        self.resize(1000, 1000)

        self.imageLabel = ImageLabel()
        self.resultLabel = QLabel()
        self.resultLabel.setFixedSize(self.imageLabel.size())
        self.resultLabel.setStyleSheet(self.imageLabel.styleSheet())

        self.minSliderLabel = QLabel('Min threshold value: 150')
        self.minSliderLabel.setFixedHeight(10)
        self.minSlider = QSlider(Qt.Horizontal, self)
        self.minSlider.setRange(0, 254)
        self.minSlider.setFocusPolicy(Qt.NoFocus)
        self.minSlider.setFixedWidth(self.width() - 2)
        self.minSlider.setValue(150)

        self.statusLabel = QLabel('Drag and drop image to find contours')

        layout = QGridLayout()
        layout.addWidget(self.imageLabel, 0, 0)
        layout.addWidget(self.resultLabel, 0, 1)
        layout.addWidget(self.minSliderLabel, 1, 0)
        layout.addWidget(self.minSlider, 2, 0, 1, 2)
        layout.addWidget(self.statusLabel, 5, 0)

        self.setLayout(layout)

        self.minSlider.valueChanged.connect(self.updateResult)

    def updateResult(self):
        self.minSliderLabel.setText("Min threshold value {0}".format(self.minSlider.value()))

        minThresholdValue = self.minSlider.value()

        if self.imageLabel.image != None:
            img = self.imageLabel.image.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            _, thresh = cv2.threshold(gray, minThresholdValue, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img, contours, -1, (0, 255, 0))

            resultQImg = bgr2qimage(img)
            customSetPixmap(self.resultLabel, resultQImg)


app = QApplication(sys.argv)
contourViewer = ContourViewer()
contourViewer.show()
app.exec_()
