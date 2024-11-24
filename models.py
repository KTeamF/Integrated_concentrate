from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy Base와 MetaData 설정
Base = declarative_base()
metadata = Base.metadata

# 예시 테이블 정의
class ExampleTable(Base):
    __tablename__ = 'example_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

