from PyQt5.QtCore import QThread
from MainWindow import Ui_MainWindow
from SeamCarving import SeamCarving


class SavePhotoWorker(QThread):
    def __init__(self, Seam: SeamCarving):
        super(SavePhotoWorker, self).__init__()
        self.s = Seam

    def run(self):
        self.s.SaveAllPhoto()


class Worker2(QThread):
    def __init__(self, main: Ui_MainWindow):
        super(Worker2, self).__init__()
        self.UI = main

    def run(self):
        self.UI.ImagesBox.setEnabled(False)
        self.UI.imageArea.setEnabled(False)
        self.UI.startButton.setEnabled(False)
        self.UI.saveButton.setEnabled(False)
        self.UI.SeamCounter.setEnabled(False)
        self.UI.openButton.setEnabled(False)
        self.UI.startSearch()
        self.UI.ImagesBox.setEnabled(True)
        self.UI.imageArea.setEnabled(True)
        self.UI.startButton.setEnabled(True)
        self.UI.saveButton.setEnabled(True)
        self.UI.SeamCounter.setEnabled(True)
        self.UI.openButton.setEnabled(True)
