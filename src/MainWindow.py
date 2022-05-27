import SeamCarving
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import WorkerThread


class Ui_MainWindow:
    isStart = True

    def __init__(self):
        self.ImagesName = [
            "AllSeams",
            "Mini Seam",
            "H-MiniSeams",
            "RemoveSeams",
            "Origin",
            "Energy Map",
        ]
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.SeamCounter = QtWidgets.QSpinBox(self.centralwidget)
        self.ImagesBox = QtWidgets.QComboBox(self.centralwidget)
        self.SeamsLabel = QtWidgets.QLabel(self.centralwidget)
        self.openButton = QtWidgets.QPushButton(self.centralwidget)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.HorzChbutton = QtWidgets.QCheckBox(self.centralwidget)
        self.VertChbutton = QtWidgets.QCheckBox(self.centralwidget)
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.Seam = SeamCarving.SeamCarving("")
        self.imageArea = ImageArea(self.centralwidget)
        self.OriginImgPath = ""

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(786, 600)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStatusTip("")
        self.centralwidget.setObjectName("centralwidget")
        self.imageArea.setEnabled(True)
        self.imageArea.setGeometry(QtCore.QRect(10, 12, 661, 501))
        self.imageArea.setAutoFillBackground(True)
        self.imageArea.setObjectName("imageArea")
        self.startButton.setGeometry(QtCore.QRect(690, 500, 75, 23))
        self.startButton.setObjectName("startButton")
        self.stopButton.setGeometry(QtCore.QRect(690, 530, 75, 23))
        self.saveButton.setGeometry(QtCore.QRect(690, 470, 75, 23))
        self.saveButton.setObjectName("saveButton")
        self.progressBar.setGeometry(QtCore.QRect(7, 530, 671, 23))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.openButton.setGeometry(QtCore.QRect(690, 20, 75, 23))
        self.openButton.setObjectName("openButton")
        self.SeamsLabel.setGeometry(QtCore.QRect(690, 60, 41, 16))
        self.SeamsLabel.setObjectName("SeamsLabel")
        self.ImagesBox.setGeometry(QtCore.QRect(690, 120, 69, 22))
        self.ImagesBox.setObjectName("ImagesBox")
        self.HorzChbutton.setGeometry(QtCore.QRect(690, 150, 69, 22))
        self.VertChbutton.setGeometry(QtCore.QRect(690, 180, 69, 22))
        self.SeamCounter.setGeometry(QtCore.QRect(730, 60, 42, 22))
        self.SeamCounter.setObjectName("SeamCounter")
        self.SeamCounter.setProperty("value", 1)
        self.startButton.raise_()
        self.stopButton.raise_()
        self.saveButton.raise_()
        self.progressBar.raise_()
        self.openButton.raise_()
        self.SeamsLabel.raise_()
        self.ImagesBox.raise_()
        self.SeamCounter.raise_()
        self.imageArea.raise_()
        self.HorzChbutton.raise_()
        self.VertChbutton.raise_()

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 786, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.saveButton.setText("Save Photos")
        self.SeamCounter.valueChanged.connect(self.getSeamCount)
        self.SeamCounter.setRange(1, 250)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.imageArea.setAcceptDrops(True)
        self.imageArea.setStyleSheet("""QLabel{ border: 1.5px dashed #aaa }""")

        self.ImagesBox.currentIndexChanged["QString"].connect(self.SetImageName)
        self.ImagesBox.addItems(self.ImagesName)

        self.openButton.clicked.connect(self.openImage)

        self.startButton.clicked.connect(self.runLongTask)
        self.stopButton.clicked.connect(self.setStopSignal)
        self.saveButton.clicked.connect(self.saveImgAction)

        self.HorzChbutton.setChecked(True)
        self.VertChbutton.setChecked(True)
        self.HorzChbutton.stateChanged.connect(self.enableHorz)
        self.VertChbutton.stateChanged.connect(self.enableVert)

    def SetImageName(self, value):
        """'Origin', 'Energy Map', 'AllSeams', 'Mini Seam', 'H-MiniSeams', 'RemoveSeams'"""
        try:
            if value == "Origin" and len(self.OriginImgPath) != 0:
                self.setPixMapInImageArea(self.Seam.getOriginImgAsPixMap())
            if value == "AllSeams" and len(self.OriginImgPath) != 0:
                self.setPixMapInImageArea(self.Seam.getAllSeamsAsPixMap())
            if value == "Energy Map" and len(self.OriginImgPath) != 0:
                self.setPixMapInImageArea(self.Seam.getEnergyMapAsPixMap())
            if value == "Mini Seam" and len(self.OriginImgPath) != 0:
                self.setPixMapInImageArea(self.Seam.getMiniSeamAsPixMap())
            if value == "H-MiniSeams" and len(self.OriginImgPath) != 0:
                self.setPixMapInImageArea(self.Seam.getHistoryMiniSeamsAsPixMap())
            if value == "RemoveSeams" and len(self.OriginImgPath) != 0:
                self.setPixMapInImageArea(self.Seam.getRemovedSeamAsPixMap())
        except Exception as e:
            SeamCarving.logging.exception(e.__class__.__name__)

    def enableHorz(self, val):
        if val == 2:
            self.Seam.HorzEnable = True
        else:
            self.Seam.HorzEnable = False

    def enableVert(self, val):
        if val == 2:
            self.Seam.VertEnable = True
        else:
            self.Seam.VertEnable = False

    def setStopSignal(self):
        self.Seam.stopSignal = True

    def getSeamCount(self):
        try:
            self.Seam.c = self.SeamCounter.value()
        except Exception as e:
            SeamCarving.logging.exception(e.__class__.__name__)

    def startSearch(self):
        self.Seam.startSearch()

    def setImageInImageArea(self):
        self.imageArea.setImgPath(self.OriginImgPath)
        self.imageArea.setPixmap(
            QPixmap(self.OriginImgPath).scaled(
                self.imageArea.width(), self.imageArea.height(), Qt.KeepAspectRatio
            )
        )

    def setPixMapInImageArea(self, img):
        self.imageArea.setPixmap(
            img.scaled(
                self.imageArea.width(), self.imageArea.height(), Qt.KeepAspectRatio
            )
        )

    def openImage(self):
        self.OriginImgPath = QFileDialog.getOpenFileName(
            filter="*.jpg " + "*.png" + "*.jpeg"
        )[0]
        if len(self.OriginImgPath) != 0:
            print("File Name is: ", self.OriginImgPath)
            self.Seam.UpdatePhoto(self.OriginImgPath)
            self.setImageInImageArea()

    def getOriginImagePath(self):
        return self.OriginImgPath

    def setOriginImagePath(self, path):
        self.OriginImgPath = path

    def ProgressingAction(self, val):
        self.progressBar.setValue(val)
        if val > 100:
            self.progressBar.setValue(0)

    def StatusAction(self, val):
        self.progressBar.setFormat(val)

    def runLongTask(self):
        try:
            if len(self.imageArea.getImgPath()) != 0:
                self.OriginImgPath = self.imageArea.getImgPath()
                self.Seam.UpdatePhoto(self.OriginImgPath)
                self.workedThred = WorkerThread.Worker2(self)
                self.workedThred.start()
                self.Seam.signal.connect(self.ProgressingAction)
                self.Seam.signalToStat.connect(self.StatusAction)
            else:
                self.messToUser("No Photo Open", "Please Select A Photo")
        except Exception as e:
            SeamCarving.logging.exception(e.__class__.__name__)

    def messToUser(self, head, mess):
        self.msg = QMessageBox()
        self.msg.setWindowTitle(head)
        self.msg.setText(mess)
        self.msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.msg.setIcon(QMessageBox.Icon.Warning)
        self.msg.exec_()

    def saveImgAction(self):
        if len(self.OriginImgPath) != 0 or self.Seam.MiniSeam is not None:
            self.wr = WorkerThread.SavePhotoWorker(self.Seam)
            self.wr.start()
            self.messToUser("Images", "Images Have Saved Successfully")
        else:
            self.messToUser("No Images To Save", "Please Select An Image Before Save")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.imageArea.setStatusTip(
            _translate("MainWindow", "Image Area You Can Drag And Drop An Image")
        )
        self.imageArea.setText(
            _translate(
                "MainWindow",
                "                                                                                       DRAG&DROP AN IMAGE",
            )
        )
        self.startButton.setStatusTip(
            _translate("MainWindow", "Push Start Button To Start The Magic")
        )
        self.startButton.setText(_translate("MainWindow", "start"))
        self.stopButton.setStatusTip(_translate("MainWindow", "Stop Looking For Seams"))
        self.stopButton.setText(_translate("MainWindow", "stop"))
        self.saveButton.setText(_translate("MainWindow", "Save Photos"))
        self.openButton.setStatusTip(
            _translate("MainWindow", "Let's Search For An Image")
        )
        self.openButton.setText(_translate("MainWindow", "open"))
        self.SeamsLabel.setText(_translate("MainWindow", "Seams:"))
        self.HorzChbutton.setText(_translate("MainWindow", "Horizontal"))
        self.VertChbutton.setText(_translate("MainWindow", "Vertical"))
        self.ImagesBox.setStatusTip(
            _translate("MainWindow", "Select One Of The Images to Display")
        )
        self.SeamCounter.setStatusTip(
            _translate("MainWindow", "Enter The Number Of Seams Wish To Remove")
        )


class ImageArea(QLabel):
    def __init__(self, t):
        super().__init__(t)
        self.OriginImgPath = ""

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.mimeData().hasImage:
            e.accept()
        else:
            e.ignore()

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasImage:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if e.mimeData().hasImage:
            e.setDropAction(Qt.CopyAction)
            self.OriginImgPath = e.mimeData().urls()[0].toLocalFile()
            self.setPixmap(
                QPixmap(self.OriginImgPath).scaled(
                    self.width(), self.height(), Qt.KeepAspectRatio
                )
            )
            e.accept()
        else:
            e.ignore()

    def setPixmap(self, a0: QtGui.QPixmap) -> None:
        super(ImageArea, self).setPixmap(a0)

    def getImgPath(self):
        return self.OriginImgPath

    def setImgPath(self, path):
        self.OriginImgPath = path


if __name__ == "__main__":
    import sys

    try:
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        SeamCarving.logging.exception(e.__class__.__name__)
