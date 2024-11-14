# Integrated_CapstoneDesign

## Motivation 🧐
<!--변경 사항 및 관련 이슈에 대한 설명란 -->
- 실시간으로 학생들의 집중도를 모니터링하고 분석하기 위한 시스템 개발, 이를 통해 교육의 질을 향상시키고 학습 효과를 극대화
- 데이터 수집의 어려움: 학생들의 얼굴 표정과 행동을 정량적으로 측정후 DB저장
- 자동화된 데이터 처리: Apache Airflow와 Docker를 이용하여 데이터를 실시간으로 처리하고 저장하는 파이프라인을 구축

<br>

## To Reviewrs ✍🏻
- 실시간 데이터 처리: 데이터가 수집되면 즉시 처리 및 분석
- 자동화된 파이프라인: Airflow와 Docker를 통해 데이터 처리와 저장이 자동화되어 효율적이고 신뢰성 있는 시스템 운영이 가능
- 데이터 통합 및 시각화: MongoDB와 Flask를 활용하여 데이터를 통합하고, 대시보드를 통해 실시간으로 시각화


<br>

# ⚒️ 전체 프로젝트 전체 구조
```bash
project-root/
│
├── dags/
│   └── data_pipeline_dag.py           # Airflow DAG 파일, 전체 데이터 파이프라인을 정의
│
├── logs/
│   ├── object_detection/
│   │   └── ...                         # RTSP 스트림 객체 탐지 정보
│   └── json/
│       └── ...                         # JSON 형식으로 변환된 데이터
│
├── src/
│   ├── detect_vehicles.py              # RTSP 스트림에서 객체를 탐지
│   ├── save_detection_info.py          # 탐지된 정보를 로그 폴더에 저장
│   ├── convert_to_json.py              # 탐지 정보 JSON으로 변환
│   ├── store_in_mongodb.py             # JSON 데이터를 MongoDB에 저장
│   └── app.py                          # Flask 서버 및 대시보드
│
├── Dockerfile                          # Docker 이미지 빌드를 위한 설정 파일
├── docker-compose.yml                  # Docker Compose 설정 파일
├── requirements.txt                    # Python 패키지 의존성

``` 
