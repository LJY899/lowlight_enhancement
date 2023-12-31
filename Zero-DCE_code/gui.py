import sys
import os
import cv2
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem, QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QRadioButton, QFrame, QGraphicsView, QGraphicsScene, QFileDialog, QGraphicsPixmapItem, QMainWindow, QTextEdit, \
    QButtonGroup
from PyQt5.QtCore import Qt, QUrl
import subprocess
from PyQt5.QtGui import QPixmap, QFont



class LowLightProcessorApp(QMainWindow):
    def __init__(self):
        super(LowLightProcessorApp, self).__init__()

        self.image_path = None
        self.video_path=None
        self.result_image_path = None
        self.result_video_path = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('LowLightProcessorApp')
        self.setGeometry(100, 100, 1600, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # 第一层：标题label
        self.title_label = QLabel("低光图片/视频处理器")
        self.title_label.setFixedHeight(30)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = self.title_label.font()
        font.setBold(True)
        font.setPointSize(14)
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
        self.file_path_textbox.setFixedHeight(24)
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
        # 创建单选按钮组
        self.button_group = QButtonGroup(self)
        self.capture_btn = QPushButton("拍照")
        self.capture_btn.setFixedWidth(93)
        self.image_radio = QRadioButton("图片处理")
        self.image_radio.setFixedWidth(150)
        self.video_radio = QRadioButton("视频处理")
        self.button_group.addButton(self.image_radio, 1)
        self.button_group.addButton(self.video_radio, 2)

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
        font.setPointSize(10)
        self.left_label.setFont(font)
        # self.scene_original = QGraphicsScene()
        # self.view_original = QGraphicsView(self.scene_original)
        self.view_original = QLabel(self)
        # self.view_original.setGeometry(QtCore.QRect(100, 180, 650, 650))
        self.view_original.setFixedHeight(650)
        self.view_original.setStyleSheet("QLabel { border: 2px solid gray; }")
        self.view_original.setScaledContents(True)

        self.left_layout = QVBoxLayout()
        self.left_layout.addWidget(self.left_label)
        self.left_layout.addWidget(self.view_original)
        process_layout.addLayout(self.left_layout)

        self.right_label = QLabel("处理后")
        self.right_label.setAlignment(Qt.AlignCenter)
        font = self.right_label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.right_label.setFont(font)
        # self.scene_processed = QGraphicsScene()
        # self.view_processed = QGraphicsView(self.scene_processed)
        self.view_processed = QLabel(self)
        self.view_processed.setFixedHeight(650)
        self.view_processed.setStyleSheet("QLabel { border: 2px solid gray; }")
        self.view_processed.setScaledContents(True)

        self.right_layout = QVBoxLayout()

        self.right_layout.addWidget(self.right_label)
        self.right_layout.addWidget(self.view_processed)
        process_layout.addLayout(self.right_layout)

        self.central_widget.setLayout(main_layout)

    def open_file(self):
        selected_button = self.button_group.checkedButton()
        if selected_button == self.image_radio:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '',
                                                       'Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)',
                                                       options=options)
            if file_name:
                self.image_path = file_name
                self.file_path_textbox.clear()
                self.file_path_textbox.append(f'Image Path: {self.image_path}')

                # Save original image
                original_image = cv2.imread(self.image_path)
                original_folder = "test"
                os.makedirs(original_folder, exist_ok=True)
                original_file = os.path.join(original_folder, 'image.jpg')
                cv2.imwrite(original_file, original_image)

                # Display original image in GraphicsView
                pixmap = QPixmap(self.image_path)
                self.view_original.setPixmap(pixmap)
                self.view_original.adjustSize()

        if selected_button == self.video_radio:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_name, _ = QFileDialog.getOpenFileName(self, 'Open Video File', '',
                                                       'Videos (*.mp4 *.avi *.mkv);;All Files (*)',
                                                       options=options)
            if file_name:
                self.video_path = file_name
                self.file_path_textbox.clear()
                self.file_path_textbox.append(f'Video Path: {self.video_path}')
                video = cv2.VideoCapture(self.video_path)
                # 获取输入视频的宽度
                width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                # 获取输入视频的高度
                height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # 获取视频帧数
                frame_number = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                # 获取输入视频的帧率
                frame_rate = int(video.get(cv2.CAP_PROP_FPS))

                ratio1 = width / 500  # (label 宽度)
                ratio2 = height / 650  # (label 高度)
                ratio = max(ratio1, ratio2)

                while video.isOpened():
                    ret, frame = video.read()
                    # 将图片转换为 Qt 格式
                    # QImage:QImage(bytes,width,height,format)
                    picture = QtGui.QImage(frame, width, height, 3 * width, QtGui.QImage.Format_RGB888)
                    pixmap = QtGui.QPixmap.fromImage(picture)
                    # 按照缩放比例自适应 label 显示
                    pixmap.setDevicePixelRatio(ratio)
                    self.view_original.setPixmap(pixmap)
                    self.view_original.show()
                    cv2.waitKey(10)
                video.release()


    def process(self):
        selected_button = self.button_group.checkedButton()
        if selected_button == self.image_radio:
            if self.image_path:
                processed_image_path = self.process_image(self.image_path)


                # Display processed image in GraphicsView
                pixmap = QtGui.QPixmap(processed_image_path).scaled(self.view_original.size(),
                                                               aspectRatioMode=Qt.KeepAspectRatio)

                item = QGraphicsPixmapItem(pixmap)
                self.scene_processed.clear()
                self.scene_processed.addItem(item)

        if selected_button == self.video_radio:
            if self.video_path:
                processed_video_path = self.process_video(self.video_path)

                video = cv2.VideoCapture(processed_video_path)
                # 获取输入视频的宽度
                width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                # 获取输入视频的高度
                height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # 获取视频帧数
                frame_number = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                # 获取输入视频的帧率
                frame_rate = int(video.get(cv2.CAP_PROP_FPS))

                ratio1 = width / 500  # (label 宽度)
                ratio2 = height / 650  # (label 高度)
                ratio = max(ratio1, ratio2)

                while video.isOpened():
                    ret, frame = video.read()
                    # 将图片转换为 Qt 格式
                    # QImage:QImage(bytes,width,height,format)
                    picture = QtGui.QImage(frame, width, height, 3 * width, QtGui.QImage.Format_BGR888)
                    pixmap = QtGui.QPixmap.fromImage(picture)
                    # 按照缩放比例自适应 label 显示
                    pixmap.setDevicePixelRatio(ratio)
                    self.view_processed.setPixmap(pixmap)
                    self.view_processed.show()
                    cv2.waitKey(10)
                video.release()

    def process_image(self, image_path):
        # 运行外部脚本，并传递图片路径
        subprocess.run(["python", "lowlight_test_1.py", image_path])

        # 处理完成后将结果保存到一个新的文件
        return "C://Desktop//result//image.jpg"

    def process_video(self, video_path):
        # 运行外部脚本，并传递图片路径
        subprocess.run(["python", "lowlight_video_test_1.py", video_path])

        # 处理完成后将结果保存到一个新的文件
        return "D://Desktop//process//video//result//video.mp4"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LowLightProcessorApp()
    window.show()
    sys.exit(app.exec_())

