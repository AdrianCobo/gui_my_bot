#!/usr/bin/env python
import rclpy

import sys
import numpy as np
import cv2

from sensor_msgs.msg import Image
from std_msgs.msg import Float64
from gazebo_msgs.msg import LinkStates

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QGraphicsScene, QMainWindow, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from main_window_ui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Image subscribers
        self.chasisSub = ImageSubscriber("/robot/chasis/image_raw")

        # Connect the image_callback
        self.chasisSub.image_callback.connect(self.update_chasis_image)

    def update_chasis_image(self, qpixmap):
        resized_pixmap = qpixmap.scaledToWidth(self.ui.Frontal_img.width())
        scene = QGraphicsScene()
        scene.addPixmap(resized_pixmap)
        self.ui.Frontal_img.setScene(scene)

    def closeEvent(self, event):
        self.chasisSub.unsubscribe()
        super(MainWindow, self).closeEvent(event)


class ImageSubscriber(QtCore.QObject):
    image_callback = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, topic):
        super(ImageSubscriber, self).__init__()

        self.image_sub = rclpy.Subscriber(topic, Image, self.handle_image)

    def handle_image(self, msg):
        # Convert ROS image message to QPixmap
        qimage = QtGui.QImage(msg.data, msg.width,
                              msg.height, QtGui.QImage.Format_RGB888)
        qpixmap = QtGui.QPixmap.fromImage(qimage)

        # Emit the signal with the updated QPixmap
        self.image_callback.emit(qpixmap)

    def unsubscribe(self):
        self.image_sub.unregister()
