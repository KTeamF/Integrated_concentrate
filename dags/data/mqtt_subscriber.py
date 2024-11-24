import paho.mqtt.client as mqtt
import json
import os

topic = "focusdata"
broker_address = "172.20.10.10"
port = 1884

username = "wjdqlscho"
password = "20010506"

logs_dir = '/Users/wjdqlscho/PycharmProjects/Capstone_Final/logs'

def mqtt_subscriber_save():
    def connecting_broker(client, userdata, flags, reason_code):
        if reason_code == 0:
            print("성공적으로 연결")
            client.subscribe("focusdata")
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
