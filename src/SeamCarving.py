import time
import numpy as np
import PIL.Image as ImageReader
import cv2
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QImage
import os
import logging


class SeamCarving(QObject):
    signal = pyqtSignal(int)
    signalToStat = pyqtSignal(str)

    def __init__(self, path: str):
        super(SeamCarving, self).__init__()
        self.currentItr = 1
        self.c = 1
        self.HorzEnable = True
        self.VertEnable = True
        self.stopSignal = False
        logging.basicConfig(
            filename="SeamCarving.log",
            filemode="a",
            level=logging.DEBUG,
            format="%(levelname)s - %(asctime)s - %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
        )
        if path != None and len(path) != 0:
            self.path = path
            self.OriginImg = ImageReader.open(path)
            self.OriginImg = np.array(self.OriginImg)
            self.History_MiniSeams = self.OriginImg.copy()
            self.ModImg = self.OriginImg.copy()

    def setPath(self, path):
        self.path = path

    def getPath(self):
        return self.path

    def UpdatePhoto(self, path):
        if path != None:
            self.path = path
            self.OriginImg = ImageReader.open(path)
            self.OriginImg = np.array(self.OriginImg)
            self.History_MiniSeams = self.OriginImg.copy()
            self.ModImg = self.OriginImg.copy()

    def get_Energy_Img(self, img, Ksize):
        energy_mapx = self.get_Energy_V(img, Ksize)
        energy_mapy = self.get_Energy_H(img, Ksize)
        return cv2.addWeighted(
            src1=energy_mapx, alpha=0.5, src2=energy_mapy, beta=0.5, gamma=0
        )

    def get_Energy_V(self, img, Ksize):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gr1 = gray.copy()
        return cv2.Sobel(gr1, cv2.CV_16S, 1, 0, ksize=Ksize)

    def get_Energy_H(self, img, Ksize):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gr1 = gray.copy()
        return cv2.Sobel(gr1, cv2.CV_16S, 0, 1, ksize=Ksize)

    def getMinIndexOnRow(self, x, y, length):
        if y >= self.energymap.shape[1]:
            y = self.energymap.shape[1] - 1
        arr2 = range(y, y + length + 1)
        try:
            arr = [self.energymap[x, value] for value in arr2]
        except IndexError:
            arr = [
                self.energymap[x, self.energymap.shape[1] - 2],
                self.energymap[x, self.energymap.shape[1] - 1],
            ]
        dic = dict()
        for i in range(len(arr2)):
            dic[arr[i]] = arr2[i]
        mini = min(arr)
        return [x, dic[mini], mini]

    def getMinIndexOnColumn(self, x, y, length):
        if x >= self.energymap.shape[0]:
            x = self.energymap.shape[0] - 1
        arr2 = range(x, x + length + 1)
        try:
            arr = [self.energymap[value, y] for value in arr2]
        except IndexError:
            arr = [
                self.energymap[self.energymap.shape[0] - 2, y],
                self.energymap[self.energymap.shape[0] - 1, y],
            ]
        dic = dict()
        for i in range(len(arr2)):
            dic[arr[i]] = arr2[i]
        mini = min(arr)
        return [dic[mini], y, mini]

    def find_Vertical_Seam(self, x: int, y: int):
        sz = self.energymap.shape
        if x >= sz[0]:
            x = sz[0] - 1
            if y < 0:
                y = 0
            elif y >= sz[1]:
                y = sz[1] - 1
            return [x, y, self.energymap[x, y]]
        prevY, currY, nextY = y - 1, y, y + 1
        if prevY < 0:
            lis = self.getMinIndexOnRow(x, y, 1)
        elif nextY >= sz[1]:
            lis = self.getMinIndexOnRow(x, prevY, 1)
        else:
            lis = self.getMinIndexOnRow(x, prevY, 2)
        return lis

    def find_Horizontal_Seam(self, x: int, y: int):
        sz = self.energymap.shape
        if x >= sz[0]:
            x = sz[0] - 1
            if y < 0:
                y = 0
            elif y >= sz[1]:
                y = sz[1] - 1
            return [x, y, self.energymap[x, y]]
        prevX, currX, nextX = x - 1, x, x + 1
        if prevX < 0:
            lis = self.getMinIndexOnColumn(x, y, 1)
        elif nextX >= sz[0]:
            lis = self.getMinIndexOnColumn(prevX, y, 1)
        else:
            lis = self.getMinIndexOnColumn(prevX, y, 2)
        return lis

    def vertical_Seam(self, originImg: np.ndarray):
        self.AllV_seams = list()
        self.lessVSeam = list()
        length = originImg.shape[1]
        for j in range(originImg.shape[1]):
            y = j
            self.V_seam = list()
            counter = 0
            for i in range(0, originImg.shape[0]):
                rr = self.find_Vertical_Seam(i, y)
                y = rr[1]
                counter -= rr[2]
                self.V_seam.append(rr)

            self.AllV_seams.append([counter, self.V_seam])
            if len(self.lessVSeam) == 0:
                self.lessVSeam = self.AllV_seams[0]
            elif self.lessVSeam[0] > counter:
                self.lessVSeam = [counter, self.V_seam]

            var = (j / length) * 100
            self.signal.emit(var)
            self.signalToStat.emit(
                f"Iter: {self.currentItr}|Finding Vertical Seam: {int(var)}%"
            )
        self.signalToStat.emit("")

    def Horizontal_Seam(self, originImg: np.ndarray):
        self.AllH_seams = list()
        self.lessHSeam = list()
        length = originImg.shape[0]
        for j in range(originImg.shape[0]):
            x = j
            self.H_seam = list()
            counter = 0
            for i in range(0, originImg.shape[1]):
                rr = self.find_Horizontal_Seam(x, i)
                x = rr[0]
                counter -= rr[2]
                self.H_seam.append(rr)

            self.AllH_seams.append([counter, self.H_seam])
            if len(self.lessHSeam) == 0:
                self.lessHSeam = self.AllH_seams[0]
            elif self.lessHSeam[0] > counter:
                self.lessHSeam = [counter, self.H_seam]

            var = (j / length) * 100
            self.signal.emit(var)
            self.signalToStat.emit(
                f"Iter: {self.currentItr}|Finding Horizontal Seam: {int(var)}%"
            )
        self.signalToStat.emit("")

    def color_Seam(self, img1, color, seam):
        for i in seam[1]:
            img1[i[0], i[1], :] = color

    def remove_vertical_seam(self, originImg: np.ndarray, **kwargs):
        if "seam" in kwargs:
            self.V_seam = kwargs["seam"][1]
        ac = 0
        length = len(self.V_seam)
        for node in self.V_seam:
            i = node[1]
            k = node[0]
            while i < originImg.shape[1] - 1:
                try:
                    temp = originImg[k, i, :].copy()
                    originImg[k, i, :] = originImg[k, i + 1, :].copy()
                    originImg[k, i + 1, :] = temp
                    i += 1
                except IndexError as e:
                    logging.exception(e.__class__.__name__)
                    break
            ac += 1
            var = (ac / length) * 100
            self.signal.emit(var)
            self.signalToStat.emit(
                f"Iter: {self.currentItr}|Remove Vertical Seam: {int(var)}%"
            )
        self.signalToStat.emit("")

    def remove_Horizontal_seam(self, originImg: np.ndarray, **kwargs):
        if "seam" in kwargs:
            self.H_seam = kwargs["seam"][1]
        ac = 0
        length = len(self.H_seam)
        for node in self.H_seam:
            i = node[0]
            k = node[1]
            while i < originImg.shape[0] - 1:
                try:
                    temp = originImg[i, k, :].copy()
                    originImg[i, k, :] = originImg[i + 1, k, :].copy()
                    originImg[i + 1, k, :] = temp
                    i += 1
                except IndexError as e:
                    logging.exception(e.__class__.__name__)
                    break
            ac += 1
            var = (ac / length) * 100
            self.signal.emit(var)
            self.signalToStat.emit(
                f"Iter: {self.currentItr}|Remove Horizontal Seam: {int(var)}%"
            )

        self.signalToStat.emit("")

    def shrinkImg(self, rows=0, columns=0):
        sz = self.ModImg.shape
        self.ModImg = self.ModImg[0 : sz[0] - rows, 0 : sz[1] - columns, :].copy()

    def Color_All_SeamInImage(self):
        self.allseam = self.ModImg.copy()
        logging.debug(f"Coloring Iter: {self.currentItr}")
        if self.HorzEnable:
            len1 = len(self.AllH_seams)
            ac = 0
            for ele in self.AllH_seams:
                self.color_Seam(self.allseam, [0, 0, 255], ele)
                ac += 1
                var = (ac / len1) * 100
                self.signal.emit(var)
                self.signalToStat.emit(
                    f"Iter: {self.currentItr}|Coloring All Horizontal Seams: {int(var)}%"
                )

        if self.VertEnable:
            len2 = len(self.AllV_seams)
            ac = 0
            for ele in self.AllV_seams:
                self.color_Seam(self.allseam, [255, 0, 0], ele)
                ac += 1
                var = (ac / len2) * 100
                self.signal.emit(var)
                self.signalToStat.emit(
                    f"Iter: {self.currentItr}|Coloring All Vertical Seams: {int(var)}%"
                )

        self.MiniSeam = self.ModImg.copy()
        if self.VertEnable:
            self.color_Seam(self.MiniSeam, [0, 255, 255], self.lessVSeam)
        if self.HorzEnable:
            self.color_Seam(self.MiniSeam, [0, 255, 255], self.lessHSeam)

        if self.VertEnable:
            self.color_Seam(self.History_MiniSeams, [0, 255, 255], self.lessVSeam)
        if self.HorzEnable:
            self.color_Seam(self.History_MiniSeams, [0, 255, 255], self.lessHSeam)
        self.signalToStat.emit(f"Iter: {self.currentItr}")

    def startSearch(self, Technique=1):
        try:
            if Technique == 1 and (self.HorzEnable or self.VertEnable):
                for i in range(self.c):
                    if not self.stopSignal:
                        self.currentItr = i + 1
                        if self.HorzEnable:
                            self.energymap = self.get_Energy_H(self.ModImg, Ksize=5)
                            self.Horizontal_Seam(self.ModImg)
                            self.remove_Horizontal_seam(
                                self.ModImg, seam=self.lessHSeam
                            )
                        if self.VertEnable:
                            self.energymap = self.get_Energy_V(self.ModImg, Ksize=5)
                            self.vertical_Seam(self.ModImg)
                            self.remove_vertical_seam(self.ModImg, seam=self.lessVSeam)
                            self.Color_All_SeamInImage()
                        if self.VertEnable and self.HorzEnable:
                            self.shrinkImg(rows=1, columns=1)
                        elif self.HorzEnable:
                            self.shrinkImg(rows=1)
                        elif self.VertEnable:
                            self.shrinkImg(columns=1)
                self.currentItr = 0
                self.stopSignal = False
            elif Technique == 2:
                for i in range(self.SeamCount):
                    self.currentItr = i
                    self.energymap = self.get_Energy_Img(self.ModImg, Ksize=5)
                    self.Horizontal_Seam(self.ModImg)
                    self.remove_Horizontal_seam(self.ModImg, seam=self.lessHSeam)
                    self.vertical_Seam(self.ModImg)
                    self.remove_vertical_seam(self.ModImg, seam=self.lessVSeam)
                    self.Color_All_SeamInImage()
                    self.shrinkImg(rows=1, columns=1)
            self.currentItr = 0
        except Exception as e:
            logging.exception(e.__class__.__name__)

    def getOriginImgAsPixMap(self):
        h, w, c = self.OriginImg.shape
        QImg = QImage(self.OriginImg.data, w, h, 3 * w, QImage.Format_RGB888)
        return QPixmap(QImg)

    def getEnergyMapAsPixMap(self):
        try:
            img = ImageReader.fromarray(self.energymap).convert("RGB")
            img.save("energymap.jpg")
            qpix = QPixmap("energymap.jpg")
            os.remove("energymap.jpg")
            return qpix
        except Exception as e:
            logging.exception(e.__class__.__name__)

    def getHistoryMiniSeamsAsPixMap(self):
        try:
            h, w, c = self.History_MiniSeams.shape
            QImg = QImage(
                self.History_MiniSeams.data, w, h, 3 * w, QImage.Format_RGB888
            )
            return QPixmap(QImg)
        except Exception as e:
            logging.exception(e.__class__.__name__)

    def getAllSeamsAsPixMap(self):
        try:
            h, w, c = self.allseam.shape
            QImg = QImage(self.allseam.data, w, h, 3 * w, QImage.Format_RGB888)
            return QPixmap(QImg)
        except Exception as e:
            logging.exception(e.__class__.__name__)

    def getMiniSeamAsPixMap(self):
        try:
            h, w, c = self.MiniSeam.shape
            QImg = QImage(self.MiniSeam.data, w, h, 3 * w, QImage.Format_RGB888)
            return QPixmap(QImg)
        except Exception as e:
            logging.exception(e.__class__.__name__)

    def getRemovedSeamAsPixMap(self):
        try:
            h, w, c = self.ModImg.shape
            QImg = QImage(self.ModImg.data, w, h, 3 * w, QImage.Format_RGB888)
            return QPixmap(QImg)
        except Exception as e:
            logging.exception(e.__class__.__name__)

    def SaveAllPhoto(self):
        t = time.localtime()
        parent = (
            "Images "
            + str(t.tm_year)
            + str(t.tm_mon)
            + str(t.tm_mday)
            + ","
            + str(t.tm_hour)
            + str(t.tm_min)
            + str(t.tm_sec)
        )
        try:
            if parent not in os.listdir("."):
                os.mkdir(parent)
            origImg = ImageReader.fromarray(self.OriginImg)
            origImg.save(os.path.join(parent, "Original.jpg"))

            MiniSeamImg = ImageReader.fromarray(self.MiniSeam)
            MiniSeamImg.save(os.path.join(parent, "MiniSeam.jpg"))

            energyImg = ImageReader.fromarray(self.energymap).convert("RGB")
            energyImg.save(os.path.join(parent, "Energy.jpg"))

            AllSeamsImg = ImageReader.fromarray(self.allseam)
            AllSeamsImg.save(os.path.join(parent, "AllSeams.jpg"))

            HMSeamsImg = ImageReader.fromarray(self.History_MiniSeams)
            HMSeamsImg.save(os.path.join(parent, "HistoryMiniSeams.jpg"))

            ModImg = ImageReader.fromarray(self.ModImg)
            ModImg.save(os.path.join(parent, "RemovedSeams.jpg"))
        except Exception as e:
            logging.exception(e.__class__.__name__)
