import cv2
import sys
import numpy as np


def Contrast_and_Brightness(alpha, beta, img):
    blank = np.zeros(img.shape, img.dtype)
    dst = cv2.addWeighted(img, alpha, blank, 1-alpha, beta)
    return dst

# 读取视频
input_video_path = sys.argv[1]
output_video_path = sys.argv[2]

# 打开视频文件
cap = cv2.VideoCapture(input_video_path)

# 检查视频是否成功打开
if not cap.isOpened():
    print("Error opening video file.")
    sys.exit()

# 视频信息
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
codec = cv2.VideoWriter_fourcc(*'mp4v')

# 输出视频
out = cv2.VideoWriter(output_video_path, codec, fps, (frame_width, frame_height))

while True:
    ret, frame = cap.read()

    if not ret:
        break

    gray_frame = Contrast_and_Brightness(2.3, 30, frame)
    # 写入处理后的帧到输出视频
    out.write(gray_frame)

# 释放资源
cap.release()
out.release()
cv2.destroyAllWindows()