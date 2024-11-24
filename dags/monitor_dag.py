import os
import subprocess
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from datetime import datetime
from dags.data.mqtt_subscriber import mqtt_subscriber_save
from dags.data.store_mongodb import save_to_mongodb_task as mongodb_task_function
import sys

sys.path.append(os.path.abspath('/Users/wjdqlscho/airflow_venv/dags'))

# JSON 파일 경로
JSON_FILE_PATH = "/Users/wjdqlscho/PycharmProjects/Capstone_Final/logs/Student.json"

# 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 1),
    'retries': 1,
}

# DAG 정의
dag = DAG(
    'mongo_monitor_dag',
    default_args=default_args,
    description='DAG for MongoDB Monitor',
    schedule='@once',
    catchup=False,
    tags=['mongo', 'flask', 'detect'],
)


# Flask 서버 실행 함수
def run_flask_server():
    subprocess.Popen(['python', '/Users/wjdqlscho/PycharmProjects/Capstone_Final/web_server/flask_server.py'])

# JSON 파일 감지 함수
def wait_for_json_file():
    return os.path.exists(JSON_FILE_PATH)

# MongoDB에 JSON 데이터 저장 함수
def save_to_mongodb():
    print(f"{JSON_FILE_PATH} 파일을 MongoDB에 저장합니다.")
    mongodb_task_function(JSON_FILE_PATH)  # store_mongodb에서 가져온 함수 호출


run_flask_server_task = PythonOperator(
    task_id='run_flask_server',
    python_callable=run_flask_server,
    dag=dag,
)

Server_pipeline = EmptyOperator(task_id='Server_pipeline', dag=dag)

MQTT_sensor_pipeline = EmptyOperator(task_id='MQTT_sensor_pipeline', dag=dag)

mqtt_subscriber_save_task = PythonOperator(
    task_id='mqtt_subscriber_save',
    python_callable=mqtt_subscriber_save,
    dag=dag,
)

MONGODB_pipeline = EmptyOperator(task_id='MONGODB_pipeline', dag=dag)

wait_for_json_file_task = PythonSensor(
    task_id='wait_for_json_file',
    python_callable=wait_for_json_file,
    timeout=180,  # 180초 동안 확인
    poke_interval=5,  # 5초 간격으로 확인
    mode='poke',  # 주기적으로 실행하는 모드
    dag=dag,
)

save_to_mongodb_operator = PythonOperator(
    task_id='save_to_mongodb',
    python_callable=save_to_mongodb,
    dag=dag,
)

# 태스크 의존성 설정
Server_pipeline >> run_flask_server_task
MQTT_sensor_pipeline >> mqtt_subscriber_save_task
MONGODB_pipeline >> wait_for_json_file_task >> save_to_mongodb_operator
