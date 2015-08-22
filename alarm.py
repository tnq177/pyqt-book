import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *

app = QApplication(sys.argv)

try:
    due = QTime.currentTime()
    message = "Alert!"
    if len(sys.argv) < 2:
        raise ValueError

    hours, mins, seconds = sys.argv[1].split(":")
    due = QTime(int(hours), int(mins), int(seconds))

    if not due.isValid():
        raise ValueError
    if len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
except ValueError:
    message = "Usage: alert.pyw HH:MM:SS [optional message]"  # 24hr clock

while QTime.currentTime() < due:
    time.sleep(2)

label = QLabel("<font color=red size=72><b>" + message + "</font>")
label.setWindowFlags(Qt.SplashScreen)
label.show()
print   "Fire event 'show' for label."\
        " But it will not show immediately"\
        " since the app event loops has yet to start."
time.sleep(10)
QTimer.singleShot(60000, app.quit)
app.exec_()
print   "Program starts. The show event is called 10 seconds ago but the label "\
        "should only show up now."
