import os
import subprocess
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.python import PythonSensor
from datetime import datetime
from dags.data.mqtt_subscriber import mqtt_subscriber_save
import sys

sys.path.append(os.path.abspath('/Users/wjdqlscho/airflow_venv/dags'))

JSON_FILE_PATH = "/Users/wjdqlscho/PycharmProjects/Capstone_Final/dags/data/logs/Student.json"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 1),
    'retries': 1,
}

dag = DAG(
    'mongo_monitor_dag',
    default_args=default_args,
    description='DAG for MongoDB Monitor',
    schedule='@once',
    catchup=False,
    tags=['mongo', 'flask', 'detect'],
)

def install_requirements():
    os.system('pip install -r /Users/wjdqlscho/PycharmProjects/20241016/requirements.txt')

def run_flask_server():
    subprocess.Popen(['python', '/Users/wjdqlscho/PycharmProjects/Capstone_Final/web_server/flask_server.py'])

def wait_for_json_file():
    return os.path.exists(JSON_FILE_PATH)

def save_to_mongodb():
    print(f"{JSON_FILE_PATH} 파일을 MongoDB에 저장합니다.")
    save_to_mongodb_task(JSON_FILE_PATH)

Server_pipeline = EmptyOperator(task_id='Server_pipeline', dag=dag)

install_requirements_task = PythonOperator(
    task_id='install_requirements',
    python_callable=install_requirements,
    dag=dag,
)

run_flask_server_task = PythonOperator(
    task_id='run_flask_server',
    python_callable=run_flask_server,
    dag=dag,
)

MQTT_sensor_pipeline = EmptyOperator(task_id='MQTT_sensor_pipeline', dag=dag)

mqtt_subscriber_save_task = PythonOperator(
    task_id='mqtt_subscriber_save',
    python_callable=mqtt_subscriber_save,
    dag=dag,
)

wait_for_json_file_task = PythonSensor(
    task_id='wait_for_json_file',
    python_callable=wait_for_json_file,
    timeout=6,  # 10초
    poke_interval=5,
    mode='poke',
    dag=dag,
)

save_to_mongodb_task = PythonOperator(
    task_id='save_to_mongodb',
    python_callable=save_to_mongodb,
    dag=dag,
)

Server_pipeline >> run_flask_server_task

MQTT_sensor_pipeline >> mqtt_subscriber_save_task >> wait_for_json_file_task >> save_to_mongodb_task
