import json
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.0.55"
MQTT_PORT = 1883
MQTT_TOPIC = "focusdata"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def publish_data():
    with open("Student.json", "r") as file:
        # 파일의 모든 줄을 읽고
        lines = file.readlines()
        for line in lines:
            data = json.loads(line.strip())
            client.publish(MQTT_TOPIC, json.dumps(data))
            print(f"Published: {data}")
            time.sleep(10)  # 퍼블리시 간격 조정 (필요 시)

try:
    while True:
        publish_data()
        time.sleep(10)
except KeyboardInterrupt:
    print("Publishing stopped.")
finally:
    client.disconnect()