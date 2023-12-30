import shutil

import cv2
import qdarkstyle
import torch
import torchvision
import torch.optim
import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QDialog
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture


import model
import numpy as np
import time
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QRadioButton, QFrame, QGraphicsView, QGraphicsScene, QFileDialog, QGraphicsPixmapItem, QMainWindow, QTextEdit, \
    QDesktopWidget
from PyQt5.QtCore import Qt

class LowLightProcessorApp(QMainWindow):
    def __init__(self):
        super(LowLightProcessorApp, self).__init__()

        self.image_path = None
        self.vedio_path = None
        self.result_image_path = None
        self.result_vedio_path = None
        self.photo_captured_path = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('LowLightProcessorApp')
        # Set the initial window size and center it on the screen
        window_width = 2400
        window_height = 1350
        self.setGeometry(QDesktopWidget().availableGeometry().center().x() - window_width // 2,
                         QDesktopWidget().availableGeometry().center().y() - window_height // 2,
                         window_width, window_height)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # 第一层：标题label
        self.title_label = QLabel("低光图片/视频处理器")
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setBold(True)
        font.setPointSize(18)
        self.title_label.setFont(font)
        main_layout.addWidget(self.title_label)

        # 第二层：水平线
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line1)

        # 第三层：上传文件按钮，文本框，开始按钮，保存按钮
        file_layout = QHBoxLayout()
        main_layout.addLayout(file_layout)

        self.upload_btn = QPushButton("上传文件")
        self.upload_btn.clicked.connect(self.open_file)
        self.file_path_textbox = QTextEdit()
        self.file_path_textbox.setFixedHeight(32)
        self.file_path_textbox.setReadOnly(True)
        self.start_btn = QPushButton("开始")
        self.start_btn.clicked.connect(self.process)
        self.save_btn = QPushButton("保存")

        file_layout.addWidget(self.upload_btn)
        file_layout.addWidget(self.file_path_textbox, 2)  # 文本框宽度较大
        file_layout.addWidget(self.start_btn)
        file_layout.addWidget(self.save_btn)

        # 第四层：拍照按钮和两个radio button
        camera_layout = QHBoxLayout()
        main_layout.addLayout(camera_layout)


        self.capture_btn = QPushButton("摄像机")
        self.capture_btn.setFixedWidth(100)
        self.image_radio = QRadioButton("图片处理")
        self.image_radio.setFixedWidth(150)
        self.video_radio = QRadioButton("视频处理")

        camera_layout.addWidget(self.capture_btn)
        camera_layout.addWidget(self.image_radio)
        camera_layout.addWidget(self.video_radio)


        # 第五层：水平线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        # 第六层：label和graphics view（处理前和处理后）
        process_layout = QHBoxLayout()
        main_layout.addLayout(process_layout)

        self.left_label = QLabel("处理前")
        self.left_label.setAlignment(Qt.AlignCenter)
        font = self.left_label.font()
        font.setBold(True)
        font.setPointSize(12)
        self.left_label.setFont(font)
        self.scene_original = QGraphicsScene()
        self.view_original = QGraphicsView(self.scene_original)
        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.left_label)
        self.left_layout.addWidget(self.view_original)
        process_layout.addLayout(self.left_layout)

        self.right_label = QLabel("处理后")
        self.right_label.setAlignment(Qt.AlignCenter)
        font = self.right_label.font()
        font.setBold(True)
        font.setPointSize(12)
        self.right_label.setFont(font)
        self.scene_processed = QGraphicsScene()
        self.view_processed = QGraphicsView(self.scene_processed)
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(self.right_label)
        self.right_layout.addWidget(self.view_processed)
        process_layout.addLayout(self.right_layout)

        self.central_widget.setLayout(main_layout)


    def update_image_path(self, image_path):
        # Slot to update the image_path variable
        self.image_path = image_path
        print(f"Image captured: {self.image_path}")

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '',
                                                   'Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)',
                                                   options=options)
        if file_name:
            self.image_path = file_name


            # Display original image in GraphicsView
            pixmap = QtGui.QPixmap(self.image_path).scaled(self.view_original.size(), aspectRatioMode=Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(pixmap)
            self.scene_original.clear()
            self.scene_original.addItem(item)

            # Display image path in textbox
            self.file_path_textbox.clear()
            self.file_path_textbox.append(f'Image Path: {self.image_path}')

    def process(self):
        if self.image_path:
            # Read the original image
            original_image = cv2.imread(self.image_path)

            # Call your image processing algorithm
            result_path = self.process_algorithm(self.image_path)
            processed_image = cv2.imread(result_path)

            # Save processed image
            result_folder = 'result'
            os.makedirs(result_folder, exist_ok=True)
            result_file = os.path.join(result_folder, 'processed_image.jpg')
            cv2.imwrite(result_file, processed_image)

            # Display processed image in GraphicsView
            pixmap = QtGui.QPixmap(result_file).scaled(self.view_original.size(),
                                                           aspectRatioMode=Qt.KeepAspectRatio)
            item = QGraphicsPixmapItem(pixmap)
            self.scene_processed.clear()
            self.scene_processed.addItem(item)

            # Display processed image path in textbox
            self.file_path_textbox.append(f'Processed Image Path: {result_file}')

    def process_algorithm(self, image_path):
        # Replace this with your image processing algorithm
        data_lowlight = Image.open(image_path)

        data_lowlight = (np.asarray(data_lowlight) / 255.0)
        data_lowlight = torch.from_numpy(data_lowlight).float()
        data_lowlight = data_lowlight.permute(2, 0, 1)
        data_lowlight = data_lowlight.unsqueeze(0)

        DCE_net = model.enhance_net_nopool()
        DCE_net.load_state_dict(torch.load('snapshots/Epoch99.pth', map_location=torch.device('cpu')))

        start = time.time()
        _, enhanced_image, _ = DCE_net(data_lowlight)
        end_time = (time.time() - start)
        print(end_time)

        # Save the enhanced image
        result_path = image_path.replace('test_data', 'result')
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        torchvision.utils.save_image(enhanced_image.squeeze(0), result_path)

        # For example, here we just convert the image to grayscale
        return result_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LowLightProcessorApp()
    window.show()
    sys.exit(app.exec_())

