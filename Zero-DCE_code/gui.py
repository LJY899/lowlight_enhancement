import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import cv2
import numpy as np
import torch
from PIL import Image
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import subprocess
import torch
import torchvision
import torch.optim
import os
import sys
import time
import shutil
import model
import numpy as np
from PIL import Image

class PixmapLabel(QLabel):
    def __init__(self,pixmap=None,enableBackground=True):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        if enableBackground:
            self.setStyleSheet("background-color: black;")
        self._pixmap=pixmap
 
    def resizeEvent(self, event):
        if self._pixmap is not None:
            self.adjustSize()
        
    def adjustSize(self):
        ratio = min(self.width() / self._pixmap.width(), self.height() / self._pixmap.height())
        scaled_pixmap = self._pixmap.scaled(int(self._pixmap.width() * ratio), int(self._pixmap.height() * ratio))
        self.setPixmap(scaled_pixmap)
        
    def refreshPixmap(self,pixmap):
        self._pixmap=pixmap
        self.adjustSize()
        
    def refreshImage(self,image):
        image=image.copy()
        height, width, channel = image.shape
        qimg=QImage(image,width,height,width*3,QImage.Format_BGR888)
        self._pixmap=QPixmap.fromImage(qimg)
        self.adjustSize()

class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cap=None
        self.timer=None
        self.frame=None
        self.start_camera()

    def init_ui(self):
        cap = cv2.VideoCapture(0)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))*2
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))*2
        self.setWindowTitle('摄像头')
        self.view_camera = PixmapLabel()
        self.setCentralWidget(self.view_camera)
        self.setGeometry(400, 300, width, height)
        
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(fps)
        
    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            self.view_camera.refreshImage(frame)
            self.frame=frame
        
    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()

class LowLightProcessorApp(QMainWindow):
    def __init__(self):
        super(LowLightProcessorApp, self).__init__()

        self.scene_processed = None
        self.path = None
        self.save_path = None
        self.result_image_path = None
        self.result_video_path = None
        
        self.init_ui()
        

    def init_ui(self):
        self.setWindowTitle('LowLightProcessorApp')
        self.setGeometry(400, 300, 2400, 1350)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # 第一层：标题label
        self.title_label = QLabel("低光图片/视频处理器")
        self.title_label.setFixedHeight(50)
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
        self.file_path_textbox.setFixedHeight(30)
        self.file_path_textbox.setReadOnly(True)
        self.start_btn = QPushButton("开始")
        self.start_btn.clicked.connect(self.process)
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save)
        self.play_before_btn = QPushButton("播放")
        self.play_before_btn.clicked.connect(self.playBefore)
        self.pause_before_btn = QPushButton("暂停")
        self.pause_before_btn.clicked.connect(self.pauseBefore)
        self.play_after_btn = QPushButton("播放")
        self.play_after_btn.clicked.connect(self.playAfter)
        self.pause_after_btn = QPushButton("暂停")
        self.pause_after_btn.clicked.connect(self.pauseAfter)

        file_layout.addWidget(self.upload_btn)
        file_layout.addWidget(self.file_path_textbox, 2)  # 文本框宽度较大
        file_layout.addWidget(self.start_btn)
        file_layout.addWidget(self.save_btn)

        # 第四层：拍照按钮和两个radio button
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        # 创建单选按钮组
        self.button_group = QButtonGroup(self)
        self.capture_btn = QPushButton("拍照")
        self.capture_btn.clicked.connect(self.takePhoto)
        self.capture_btn.setFixedWidth(93)
        self.camera_btn = QPushButton("摄像头")
        self.camera_btn.setFixedWidth(93)
        self.camera_btn.clicked.connect(self.camera)
        
        button_layout.addWidget(self.camera_btn)
        button_layout.addWidget(self.capture_btn)

        # 第五层：水平线
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        # 第六层：label和graphics view（处理前和处理后）
        
        process_layout = QHBoxLayout()
        main_layout.addLayout(process_layout)
        
        left_layout = QHBoxLayout()
        right_layout = QVBoxLayout()
        
        self.before_label = QLabel("处理前")
        self.before_label.setFixedHeight(50) 
        self.before_label.setAlignment(Qt.AlignCenter)
        font = self.before_label.font()
        font.setBold(True)
        font.setPointSize(13)
        self.before_label.setFont(font)
        self.view_original = PixmapLabel()
        self.before_layout = QVBoxLayout()
        self.before_layout.addWidget(self.before_label)
        self.before_layout.addWidget(self.view_original)
        self.before_button_layout = QHBoxLayout()
        self.before_button_layout.addWidget(self.play_before_btn)
        self.before_button_layout.addWidget(self.pause_before_btn)
        self.before_layout.addLayout(self.before_button_layout)

        self.after_label = QLabel("处理后")
        self.after_label.setFixedHeight(50) 
        self.after_label.setAlignment(Qt.AlignCenter)
        font = self.after_label.font()
        font.setBold(True)
        font.setPointSize(13)
        self.after_label.setFont(font)
        self.view_processed = PixmapLabel()
        
        self.after_layout = QVBoxLayout()

        self.after_layout.addWidget(self.after_label)
        self.after_layout.addWidget(self.view_processed)
        self.after_button_layout = QHBoxLayout()
        self.after_button_layout.addWidget(self.play_after_btn)
        self.after_button_layout.addWidget(self.pause_after_btn)
        self.after_layout.addLayout(self.after_button_layout)
        left_layout.addLayout(self.before_layout)
        left_layout.addLayout(self.after_layout)
        process_layout.addLayout(left_layout)
        self.central_widget.setLayout(main_layout)
        
    def camera(self):
        self.cameraWindow=CameraWindow()
        self.cameraWindow.show()
        
    def takePhoto(self):
        frame = self.cameraWindow.frame
        original_folder = "test"
        os.makedirs(original_folder, exist_ok=True)
        self.path = os.path.join('test','photo.png')
        cv2.imwrite(self.path,frame)
        self.view_original.refreshImage(frame)
        
    def start_video(self,path,label):
        cap = cv2.VideoCapture(path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_video(cap,label,timer))
        timer.start(fps)
        videoManager = [timer,cap]
        return videoManager
        
    def update_video(self,cap,label,timer):
        ret, frame = cap.read()
        if ret:
            label.refreshImage(frame)
        else:
            timer.stop()
            
    def playBefore(self):
        self.play(self.videoManagerBefore)
        
    def pauseBefore(self):
        self.pause(self.videoManagerBefore)
        
    def playAfter(self):
        self.play(self.videoManagerAfter)
        
    def pauseAfter(self):
        self.pause(self.videoManagerAfter)
            
    def play(self,videoManager):
        timer,cap = videoManager
        curFrameCount=cap.get(cv2.CAP_PROP_POS_FRAMES)
        allFrameCount=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if curFrameCount==allFrameCount:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        timer.start(fps)
        
    def pause(self,videoManager):
        timer,cap = videoManager
        timer.stop()

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '',
                                                'Files (*.png *.jpg *.jpeg *.bmp *.gif *.mp4 *.avi *.mkv);;All Files (*)',
                                                options=options)
        if file_name:
            self.path = file_name
            image=cv2.imread(file_name)
            self.file_path_textbox.clear()
            original_folder = "test"
            os.makedirs(original_folder, exist_ok=True)
            shutil.copy2(self.path, os.path.join(original_folder, os.path.basename(self.path)))
            if image is not None:
                self.file_path_textbox.append(f'Image Path: {self.path}')
                self.view_original.refreshImage(image)
            else:
                self.file_path_textbox.append(f'Video Path: {self.path}')
                self.videoManagerBefore = self.start_video(self.path,self.view_original)
                
    def save(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;All Files (*)", options=options)
        if file_name:
            self.save_path = file_name
            image=cv2.imread(self.path)
            if image is not None:
                shutil.copy2("result/image.jpg", self.save_path)
            else:
                shutil.copy2("result/video.mp4", self.save_path)

    def process(self):
        if self.path:
            image=cv2.imread(self.path)
            if image is not None:
                processed_image_path = self.process_image(self.path)
                processed_image = cv2.imread(processed_image_path)
                self.view_processed.refreshImage(processed_image)
            else:
                processed_video_path = self.process_video(self.path)
                self.videoManagerAfter = self.start_video(processed_video_path,self.view_processed)
                
    def process_image(self, image_path):
        #output_path = self.save_path if self.save_path else "result/image.jpg"
        output_path = "result/image.jpg"
        # 运行外部脚本，并传递图片路径
        #subprocess.run(["python", "lowlight_test.py", self.path, output_path])
        self.process_algorithm(self.path, output_path)
        return output_path

    def process_video(self, video_path):
        #output_path = self.save_path if self.save_path else "result/video.mp4"
        output_path = "result/video.mp4"
        # 运行外部脚本，并传递图片路径
        subprocess.run(["python", "lowlight_video_test.py", self.path, output_path])
        return output_path
        
    def process_algorithm(self, image_path, result_path):
        # Replace this with your image processing algorithm
        data_lowlight = Image.open(image_path)

        data_lowlight = (np.asarray(data_lowlight) / 255.0)
        data_lowlight = torch.from_numpy(data_lowlight).float()
        data_lowlight = data_lowlight.permute(2, 0, 1)
        data_lowlight = data_lowlight.unsqueeze(0)

        DCE_net = model.enhance_net_nopool()
        DCE_net.load_state_dict(torch.load('snapshots/Epoch99.pth',map_location=torch.device('cpu')))

        start = time.time()
        _, enhanced_image, _ = DCE_net(data_lowlight)
        end_time = (time.time() - start)
        print(end_time)

        # Save the enhanced image
        torchvision.utils.save_image(enhanced_image.squeeze(0), result_path)

        # For example, here we just convert the image to grayscale
        return result_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LowLightProcessorApp()
    window.show()
    sys.exit(app.exec_())

