import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# โหลดค่าจาก .env
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# สร้าง Engine สำหรับเชื่อมต่อ PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# สร้าง Session สำหรับทำ Transaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ออกแบบตารางเก็บข้อมูล
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, unique=True, index=True, nullable=False) # บังคับห้ามว่าง และห้ามซ้ำ
    result = Column(Text, nullable=False)
    status = Column(String, default="completed")

# สั่งสร้างตารางใน Database (ถ้ายังไม่มี)
Base.metadata.create_all(bind=engine)

# ฟังก์ชัน Generator สำหรับเรียกใช้ Database Session ใน FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()