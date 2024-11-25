import logging
import multiprocessing as multip
import os
import socket
import numpy as np
import mediapipe as mp
import tensorflow as tf
import time
from datetime import datetime
import json
from ultralytics import YOLO
import cv2

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

logging.getLogger('tensorflow').setLevel(logging.ERROR)

DEBUG_MODE = True  # 디버그 모드 설정

# YOLO 모델 로드
model = YOLO("yolo11n_float16.tflite")

# Mediapipe 설정
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# TFLite 모델 경로 및 로드
interpreter_path = 'pose_lstm_model_quantized.tflite'
interpreter = tf.lite.Interpreter(model_path=interpreter_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# JSON 저장 함수
def save_data(data):
    with open('Student.json', 'a') as f:
        json.dump(data, f)
        f.write('\n')

# 사람 감지 함수
def detect_persons(frame):
    results = model(frame)
    boxes = []
    confidences = []
    for result in results:
        for box in result.boxes:
            if box.cls == 0 and box.conf > 0.5:  # Class ID 0은 '사람'
                x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0]]
                boxes.append([x1, y1, x2 - x1, y2 - y1])
                confidences.append(float(box.conf))
    return [(boxes[i], confidences[i]) for i in range(len(boxes))]

# Mediapipe와 TFLite 모델을 활용한 집중 여부 판단
def process_person(frame, box, avg_focus):
    x, y, w, h = box
    person_img = frame[y:y + h, x:x + w]
    person_img_rgb = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
    results = holistic.process(person_img_rgb)

    if results.pose_landmarks:
        keypoints = [(int(lm.x * w), int(lm.y * h)) for lm in results.pose_landmarks.landmark]
        keypoints_flat = np.array(keypoints).flatten().reshape(1, -1)
        keypoints_flat = np.pad(keypoints_flat, ((0, 0), (0, 66 - keypoints_flat.shape[1])), 'constant').reshape(
            (1, 33, 2)).astype(np.float32)

        interpreter.set_tensor(input_details[0]['index'], keypoints_flat)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        return (output_data[0][0] > 0.6, keypoints)
    else:
        return (avg_focus > 0.5, [])

# 소켓 서버에서 스트리밍 데이터 수신
def receive_stream(server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)
    print(f"Listening on {server_ip}:{server_port}...")

    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    while True:
        # 데이터 크기 수신
        data = conn.recv(4)
        if not data:
            break

        frame_size = int.from_bytes(data, byteorder='big')
        frame_data = b''

        while len(frame_data) < frame_size:
            frame_data += conn.recv(frame_size - len(frame_data))

        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        yield frame

    conn.close()
    server_socket.close()

# 메인 실행 함수
def main(server_ip, server_port):
    start_time = time.time()
    unfocused_counts = []
    persons = []
    frame_count = 0

    # 멀티프로세싱 풀 설정
    pool = multip.Pool(processes=2)

    # 소켓 스트리밍 데이터 수신
    for frame in receive_stream(server_ip, server_port):
        if frame_count % 4 == 0:
            persons = detect_persons(frame)

        avg_focus = sum(unfocused_counts) / len(unfocused_counts) if unfocused_counts else 0.5
        results_list = pool.starmap(process_person, [(frame, box, avg_focus) for box, _ in persons])

        for i, (box, confidence) in enumerate(persons):
            is_unfocused, keypoints = results_list[i]
            color = (0, 0, 255) if is_unfocused else (0, 255, 0)  # 집중 시 녹색, 미집중 시 빨간색
            x, y, w, h = box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            if is_unfocused:
                unfocused_counts.append(1)
            else:
                unfocused_counts.append(0)

        if time.time() - start_time >= 10:
            timestamp = datetime.now().isoformat()
            students = len(persons)
            unfocused_avg = sum(unfocused_counts) / len(unfocused_counts) if unfocused_counts else 0
            data = {
                "timestamp": timestamp,
                "students": students,
                "unfocused_students": unfocused_avg
            }

            save_data(data)

            unfocused_counts = []
            start_time = time.time()

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    pool.close()
    pool.join()

if __name__ == "__main__":
    SERVER_IP = '0.0.0.0'
    SERVER_PORT = 8080
    main(SERVER_IP, SERVER_PORT)
