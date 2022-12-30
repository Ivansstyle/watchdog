#! usr/bin/python3 

# requests, img show 

from time import sleep

import requests
from io import BytesIO
from PySide6 import QtCore
from PySide6.QtCore import Signal, Slot, QObject, QThread
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel
from PySide6.QtGui import QImage, QPixmap
import sys

IMG_URL = 'http://overseas.de/pferdehof/webcam/pferdehof-webcam-kaufbeuren.jpg'

REQUEST_TIME_SECS = 30


class ImagePoller(QObject):
    new_image = Signal(bytes)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.last_image = None
        self.images = []

    def get_image(self):
        res = requests.get(IMG_URL)
        image_bytes = BytesIO(res.content).read()
        self.new_image.emit(image_bytes)
        self.last_image = self.new_image
        self.images.append(self.last_image)

    def poll_images(self):
        while(True):
            print("Getting image")
            self.get_image()
            print("Waiting 30s")
            sleep(REQUEST_TIME_SECS)
            

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(1280)
        self.setFixedHeight(720)
        self.pixmap = QPixmap()
        self.widget = QLabel(self)
        self.widget.setPixmap(self.pixmap)
        self.setCentralWidget(self.widget)
        #self.layout().addWidget(self.pixmap)
        self.image_poller = ImagePoller()
        self.polling_thread = QThread()
        self.image_poller.moveToThread(self.polling_thread)
        self.image_poller.new_image.connect(self.change_image)
        self.polling_thread.started.connect(self.image_poller.poll_images)
        self.polling_thread.start()


    @Slot(bytes)
    def change_image(self, img_bytes):
        self.pixmap.loadFromData(img_bytes)
        self.widget.setPixmap(self.pixmap)


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())

