import json
import threading
import time
from datetime import datetime

import cv2
import numpy as np
import tensorflow as tf
from picamera2 import Picamera2
import mediapipe as mp
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

DEBUG_MODE = True

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)
unique_id = 0

person_ids = {}
unfocused_counts = []
start_time = time.time()

interpreter = tf.lite.Interpreter(model_path='pose_lstm_model_quantized.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def detect(pose_landmarks):
    keypoints = []
    for lm in pose_landmarks.landmark:
        x, y = int(lm.x * 640), int(lm.y * 480)
        keypoints.append((x, y))
    keypoints_flat = np.array(keypoints).flatten().reshape(1, -1)
    keypoints_flat = np.pad(keypoints_flat, ((0, 0), (0, 66 - keypoints_flat.shape[1])), 'constant')
    keypoints_flat = keypoints_flat.reshape((1, 33, 2))

    keypoints_flat = keypoints_flat.astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], keypoints_flat)

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data[0][0] > 0.7

def save_data():
    global unfocused_counts, start_time
    while True:
        if time.time() - start_time >= 10:
            timestamp = datetime.now().isoformat()
            students = len(person_ids)
            unfocused_avg = sum(unfocused_counts) / len(unfocused_counts) if unfocused_counts else 0

            data = {
                "timestamp": timestamp,
                "students": students,
                "unfocused_students": unfocused_avg
            }

            with open('Student.json', 'a') as f:
                json.dump(data, f)
                f.write('\n')

            unfocused_counts = []
            start_time = time.time()

threading.Thread(target=save_data, daemon=True).start()

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

frame_queue = []

def capture_frames():
    global frame_queue
    while True:
        frame = picam2.capture_array()
        if frame is not None:
            frame_queue.append(frame)
        if len(frame_queue) > 10:
            frame_queue.pop(0)

def process_frames():
    global frame_queue, unique_id
    while True:
        if frame_queue:
            frame = frame_queue.pop(0)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if results.pose_landmarks:
                unfocused_count = 0
                for person_idx, pose_landmarks in enumerate([results.pose_landmarks]):
                    if person_idx not in person_ids:
                        person_ids[person_idx] = unique_id
                        unique_id += 1

                    nose = pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
                    nose_coords = (int(nose.x * frame.shape[1]), int(nose.y * frame.shape[0]))

                    if detect(pose_landmarks):
                        unfocused_count += 1
                        color = (0, 0, 255)
                        print(f"unfocused: {person_ids[person_idx]}")
                    else:
                        color = (0, 255, 0)

                    cv2.putText(frame, f"ID: {person_ids[person_idx]}", (nose_coords[0] + 10, nose_coords[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                unfocused_counts.append(unfocused_count)

            if DEBUG_MODE:
                cv2.imshow("For Debug window", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

threading.Thread(target=capture_frames, daemon=True).start()
threading.Thread(target=process_frames, daemon=True).start()

try:
    while True:
        time.sleep(5)
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    picam2.stop()
    cv2.destroyAllWindows()