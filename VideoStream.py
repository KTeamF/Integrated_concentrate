import socket
import cv2
from picamera2 import Picamera2
import numpy as np

# 서버 정보
SERVER_IP = 'ipipip'  # 수신 측 IP 주소
SERVER_PORT = 8080  # 수신 측 포트

# 카메라 초기화
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# 소켓 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

try:
    while True:
        frame = picam2.capture_array()

        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        frame_size = len(frame_data)
        client_socket.sendall(frame_size.to_bytes(4, byteorder='big'))

        client_socket.sendall(frame_data)
finally:
    picam2.stop()
    client_socket.close()
