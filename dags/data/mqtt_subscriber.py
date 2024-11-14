import paho.mqtt.client as mqtt
import json
import os

topic = "focusdata"
broker_address = "192.168.0.55"  # 라즈베리파이에서 자동으로 브로커 IP를 찾을 수 있도록 수정해야 함
port = 1884  # 기본 MQTT 포트

# 사용자 이름과 비밀번호 설정 (필요한 경우)
username = "wjdqlscho"  # 본인의 사용자 이름
password = "20010506"  # 본인의 비밀번호

# 상대 경로로 로그 디렉토리 설정
logs_dir = '/Users/wjdqlscho/PycharmProjects/Capstone_Final/logs'  # 라즈베리파이에서는 /home/pi/logs 등 상대 경로로 설정

def mqtt_subscriber_save():
    def connecting_broker(client, userdata, flags, reason_code):
        if reason_code == 0:
            print("성공적으로 연결")
            client.subscribe("focusdata")  # 토픽 이름을 맞춰서 구독
        else:
            print(f"연결 실패, 코드: {reason_code}")

    def message_from_broker(client, userdata, msg):
        message = msg.payload.decode()
        print(f"받은 메시지: {message} / 토픽: {msg.topic} ")
        try:
            data = json.loads(message)
            os.makedirs(logs_dir, exist_ok=True)  # 로그 디렉토리가 없으면 생성
            with open(os.path.join(logs_dir, 'Student.json'), 'a') as f:
                json.dump(data, f)
                f.write('\n')
            print(f"저장된 데이터: {data}")
        except Exception as e:
            print(f"파일에 저장 중 오류: {e}")

    client = mqtt.Client()

    # 사용자 이름과 비밀번호 설정
    client.username_pw_set(username, password)

    client.on_connect = connecting_broker
    client.on_message = message_from_broker

    try:
        client.connect(broker_address, port, 60)
        client.loop_forever()
    except Exception as e:
        print(f"연결 오류: {e}")


if __name__ == "__main__":
    mqtt_subscriber_save()
