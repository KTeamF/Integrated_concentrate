import json
import random
import time
from pymongo import MongoClient
import certifi
from datetime import datetime

def connect_to_mongodb():
    client = MongoClient(
        'mongodb+srv://jungbin1486:j3727416!!@cluster0.auzrugj.mongodb.net/',
        tls=True,
        tlsCAFile=certifi.where()
    )
    return client['focus_data'], client['focus_data']['student_data']

def save_json(filename):
    with open(filename, 'r') as file:
        return [json.loads(line) for line in file]

def add_additional_fields(data):
    lecture_names = ["강의 1", "강의 2", "강의 3"]
    for document in data:
        document['lecture_name'] = random.choice(lecture_names)
        document['date'] = datetime.now()
    return data

def save_to_mongodb_task(filename):
    db, collection = connect_to_mongodb()
    filename = '/Users/wjdqlscho/PycharmProjects/Capstone_Final/logs/Student.json'
    data = save_json(filename)

    if data:
        data = add_additional_fields(data)

        for document in data:
            collection.insert_one(document)
            print(f"도큐먼트가 저장되었습니다: {document}")
            time.sleep(1)  # 시간 지연 줌
        print("모든 데이터가 MongoDB에 성공적으로 저장되었습니다.")
    else:
        print("저장할 데이터가 없습니다.")

if __name__ == '__main__':
    save_to_mongodb_task('/Users/wjdqlscho/PycharmProjects/Capstone_Final/logs/Student.json')