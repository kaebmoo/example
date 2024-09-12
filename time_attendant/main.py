from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
import json
import logging
import redis
from typing import Optional
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, exists
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
import os
import pytz

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=1)

# ดึงค่าจากไฟล์ .env
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# กำหนดค่าฐานข้อมูล
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

Base = declarative_base()
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    pool_size=120,  # เพิ่มจำนวน connection pool 
    max_overflow=20,  # อนุญาตให้เพิ่ม connection ได้อีก 10 ครั้งเมื่อ pool เต็ม
    pool_timeout=120  # ระยะเวลารอ connection ใหม่ (วินาที)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# ปิดการแสดงผล logging ระดับ INFO และ DEBUG สำหรับ SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# สร้างแอป FastAPI
app = FastAPI()

class AttendanceStatus(Enum):
    """คลาส Enum สำหรับสถานะการลงเวลา"""
    NORMAL = "ปกติ"
    LATE = "สาย"
    EARLY_LEAVE = "ออกก่อน"

# โมเดลของผู้ใช้ (User)
class User(Base):
    """โมเดลของผู้ใช้ (User)"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)  # เพิ่ม index ตรงนี้
    hashed_password = Column(String)

    # ความสัมพันธ์กับ Attendance
    attendances = relationship("Attendance", back_populates="user")

# คลาสสำหรับรับข้อมูล request ใน API
class UserRequest(BaseModel):
    """
    คลาส Pydantic สำหรับรับข้อมูลผู้ใช้ที่ต้องการตรวจสอบ
    
    Attributes:
        username (str): ชื่อผู้ใช้ที่ต้องการตรวจสอบ
        password (str): รหัสผ่านที่ต้องการตรวจสอบ
    """
    username: str
    password: str

class Attendance(Base):
    """โมเดล Attendance สำหรับเก็บเวลาการเข้า-ออกงาน"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, default=AttendanceStatus.NORMAL.value)

    # ความสัมพันธ์กับ User
    user = relationship("User", back_populates="attendances")

# โมเดลสำหรับ request body
class AttendanceRequest(BaseModel):
    """โมเดลสำหรับ request body สำหรับการลงเวลา"""
    username: str
    password: str
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None

# โหลดข้อมูลจาก CSV
users_data = pd.read_csv("/Users/seal/Downloads/Unique_Usernames_and_Hashed_Passwords.csv", dtype=str)

def preload_users_to_redis():
    """
    ฟังก์ชันสำหรับ preload ข้อมูล Username และ Hashed_Password จาก CSV ลงใน Redis
    """
    for index, row in users_data.iterrows():
        username = row['Username']
        hashed_password = row['Hashed_Password']
        
        # สร้างข้อมูลในรูปแบบ dictionary
        user_data = {
            "username": username,
            "hashed_password": hashed_password
        }
        
        # แปลงเป็น JSON string และเก็บลง Redis โดยใช้ username เป็น key
        redis_client.set(f"user:{username}", json.dumps(user_data))
        

# Dependency สำหรับสร้าง session
async def get_db():
    """Dependency สำหรับสร้าง session"""
    async with SessionLocal() as session:
        try:
            yield session  # ทำงานกับ session
        finally:
            await session.close()  # ปิด session หลังจากใช้งานเสร็จ


# ฟังก์ชันแปลงเวลา UTC เป็นเวลาท้องถิ่น
def convert_utc_to_local(utc_dt):
    """ฟังก์ชันแปลงเวลา UTC เป็นเวลาท้องถิ่น"""
    local_tz = pytz.timezone('Asia/Bangkok')  # ตั้งค่าเป็นเขตเวลา UTC+7
    local_dt = utc_dt.astimezone(local_tz)
    return local_dt

# ฟังก์ชันสำหรับแปลงรหัสผ่านเป็น SHA-256 hash
def verify_password_sha256(plain_password: str, hashed_password: str) -> bool:
    """
    แปลงรหัสผ่านเป็น SHA-256 hash และตรวจสอบว่าตรงกับค่า hash ที่จัดเก็บหรือไม่
    
    Args:
        plain_password (str): รหัสผ่านที่ยังไม่ได้เข้ารหัส
        hashed_password (str): รหัสผ่านที่ถูกเข้ารหัสแล้ว (ในรูปแบบ SHA-256)

    Returns:
        bool: True หากรหัสผ่านที่แปลงแล้วตรงกับ hashed_password, False หากไม่ตรง
    """
    hashed_input = hashlib.sha256(plain_password.encode()).hexdigest()
    return hashed_input == hashed_password

# ฟังก์ชันสำหรับตรวจสอบผู้ใช้
async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    ตรวจสอบว่าผู้ใช้และรหัสผ่านที่ให้มาตรงกับข้อมูลที่จัดเก็บในฐานข้อมูลหรือไม่

    Args:
        db (AsyncSession): เซสชันฐานข้อมูลสำหรับการเรียกข้อมูล
        username (str): ชื่อผู้ใช้ที่ต้องการตรวจสอบ
        password (str): รหัสผ่านที่ต้องการตรวจสอบ (ยังไม่ได้เข้ารหัส)

    Returns:
        Optional[User]: คืนค่าผู้ใช้หากตรวจสอบสำเร็จ, None หากข้อมูลไม่ถูกต้อง
    """
    # Check if the user data is already cached in Redis
    cached_user = redis_client.get(f"user:{username}")
    
    if cached_user:
        try:
            logging.info("Cache hit for user: %s", username)
            # Deserialize JSON string to a dictionary
            user_data = json.loads(cached_user)
            user = User(**user_data)  # Convert the dictionary back to a User object
        except json.JSONDecodeError:
            logging.error("Failed to decode cached data for user: %s, invalid JSON.", username)
            # If there's an error in decoding, remove the cached data and refetch from DB
            redis_client.delete(f"user:{username}")
            user = None
    else:
        logging.info("Cache miss for user: %s, fetching from DB.", username)
        # Fetch the user from the database if not cached
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        # If user exists, cache it in Redis for 5 minutes (300 seconds)
        if user:
            # Convert the user object to a dictionary (excluding internal state)
            user_data = {
                "id": user.id,
                "username": user.username,
                "hashed_password": user.hashed_password,
            }
            logging.info("Caching user: %s", username)
            # Serialize the dictionary to JSON and store in Redis
            redis_client.setex(f"user:{username}", 300, json.dumps(user_data))
    
    # Verify password
    if user and verify_password_sha256(password, user.hashed_password):
        logging.info("Password verified for user: %s", username)
        return user
    else:
        logging.warning("Invalid password for user: %s", username)
    
    return None

# ฟังก์ชันสำหรับตรวจสอบผู้ใช้
async def authenticate_user_(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    ตรวจสอบว่าผู้ใช้และรหัสผ่านที่ให้มาตรงกับข้อมูลที่จัดเก็บในฐานข้อมูลหรือไม่

    Args:
        db (AsyncSession): เซสชันฐานข้อมูลสำหรับการเรียกข้อมูล
        username (str): ชื่อผู้ใช้ที่ต้องการตรวจสอบ
        password (str): รหัสผ่านที่ต้องการตรวจสอบ (ยังไม่ได้เข้ารหัส)

    Returns:
        Optional[User]: คืนค่าผู้ใช้หากตรวจสอบสำเร็จ, None หากข้อมูลไม่ถูกต้อง
    """
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    # ตรวจสอบรหัสผ่านกับ SHA-256
    if user and verify_password_sha256(password, user.hashed_password):
        return user
    return None

# API สำหรับตรวจสอบผู้ใช้
@app.post("/check_user/")
async def check_user(user_request: UserRequest, db: AsyncSession = Depends(get_db)):
    """
    API สำหรับตรวจสอบว่าผู้ใช้มีอยู่ในระบบหรือไม่และตรวจสอบรหัสผ่านของผู้ใช้

    Args:
        user_request (UserRequest): ข้อมูลผู้ใช้ที่ประกอบด้วย username และ password
        db (AsyncSession): เซสชันฐานข้อมูลสำหรับการเรียกข้อมูล

    Returns:
        dict: คืนค่า {"status": "User exists"} หากผู้ใช้และรหัสผ่านถูกต้อง
        HTTPException: ส่งกลับข้อผิดพลาด 400 หากชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง
    """
    user = await authenticate_user(db, user_request.username, user_request.password)
    
    if user:
        return {"status": "User exists"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
# ฟังก์ชันตรวจสอบสถานะการลงเวลา
def calculate_attendance_status(check_in_time: datetime, check_out_time: Optional[datetime] = None):
    """
    ฟังก์ชันสำหรับคำนวณสถานะการลงเวลาเข้างานและออกงาน

    Args:
        check_in_time (datetime): เวลาที่พนักงานลงเวลาเข้างาน
        check_out_time (datetime, optional): เวลาที่พนักงานลงเวลาออกงาน

    Returns:
        AttendanceStatus: สถานะการลงเวลา (ปกติ, สาย, ออกก่อน)
    """
    day_shift_start = datetime.strptime("08:30", "%H:%M").time()
    day_shift_end = datetime.strptime("16:30", "%H:%M").time()
    
    status = AttendanceStatus.NORMAL
    if check_in_time.time() > day_shift_start:
        status = AttendanceStatus.LATE
    if check_out_time and check_out_time.time() < day_shift_end:
        status = AttendanceStatus.EARLY_LEAVE
    return status

# API สำหรับบันทึกเวลาเข้างาน
@app.post("/check_in/")
async def check_in(attendance_request: AttendanceRequest, db: AsyncSession = Depends(get_db)):
    """
    API สำหรับบันทึกเวลาเข้างาน

    Args:
        attendance_request (AttendanceRequest): ข้อมูลการลงเวลาจากผู้ใช้
        db (AsyncSession): Session ของฐานข้อมูล

    Returns:
        dict: ผลการบันทึกเวลาเข้างานและสถานะการลงเวลา
    """
    # ตรวจสอบว่า user มีอยู่และตรวจสอบ password
    user = await authenticate_user(db, attendance_request.username, attendance_request.password)
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid username or password")
    
    # ตรวจสอบการ check_in ใน Redis ก่อน
    cached_attendance = redis_client.get(f"attendance:checkin:{attendance_request.username}")
    if cached_attendance:
        logging.info("Cache hit for attendance check-in: %s", attendance_request.username)
        cached_data = json.loads(cached_attendance)
        return {
            "status": "already_checked_in",
            "message": "You have already checked in today.",
            "check_in_time": cached_data["check_in_time"]
        }
    
    # ดึงข้อมูล check_in ของผู้ใช้ในวันนี้จากฐานข้อมูล
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    today_end = (today_start + timedelta(days=1)).replace(tzinfo=None)

    result = await db.execute(
        select(Attendance)
        .where(Attendance.username == attendance_request.username)
        .where(Attendance.check_in >= today_start)
        .where(Attendance.check_in < today_end)
    )

    attendance = result.scalars().first()

    # ตรวจสอบว่าในวันเดียวกันมีการ check_in แล้วหรือไม่
    if attendance:
        return {
            "status": "already_checked_in",
            "message": "You have already checked in today.",
            "check_in_time": attendance.check_in.isoformat()  # แสดงเวลาที่เช็คอินแล้ว
        }

    # บันทึกเวลา check_in
    check_in_time = (attendance_request.check_in or datetime.now(timezone.utc)).replace(tzinfo=None)

    status = calculate_attendance_status(check_in_time)

    new_attendance = Attendance(username=str(user.username), check_in=check_in_time, status=status.value)

    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)
    
    # แปลงเวลาเป็นเวลาท้องถิ่นก่อนส่งกลับ
    local_check_in_time = convert_utc_to_local(new_attendance.check_in)

    # แคชข้อมูล check_in ใน Redis
    attendance_data = {
        "check_in_time": local_check_in_time.isoformat(),
        "status": status.value
    }
    redis_client.setex(f"attendance:checkin:{attendance_request.username}", 86400, json.dumps(attendance_data))  # แคชเป็นเวลา 1 วัน
    
    return {
        "status": "Check-in successful",
        "check_in": local_check_in_time.isoformat(),  # ส่งกลับในรูปแบบ ISO และแสดงเวลาท้องถิ่น
        "attendance_status": status.value
    }

# API สำหรับบันทึกเวลาออกงาน
@app.post("/check_out/")
async def check_out(attendance_request: AttendanceRequest, db: AsyncSession = Depends(get_db)):
    """
    API สำหรับบันทึกเวลาออกงาน (สามารถทำซ้ำได้ โดยจะอัปเดตเวลาล่าสุด)

    Args:
        attendance_request (AttendanceRequest): ข้อมูลการลงเวลาจากผู้ใช้
        db (AsyncSession): Session ของฐานข้อมูล

    Returns:
        dict: ผลการบันทึกเวลาออกงานและสถานะการลงเวลา
    """

    # ตรวจสอบว่า user มีอยู่และตรวจสอบ password
    user = await authenticate_user(db, attendance_request.username, attendance_request.password)
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid username or password")
    
    # ตรวจสอบการ check_out ใน Redis ก่อน
    cached_attendance = redis_client.get(f"attendance:checkout:{attendance_request.username}")
    if cached_attendance:
        logging.info("Cache hit for attendance check-out: %s", attendance_request.username)
        cached_data = json.loads(cached_attendance)
        return {
            "status": "already_checked_out",
            "message": "You have already checked out today.",
            "check_out_time": cached_data["check_out_time"]
        }

    # ดึงข้อมูลการ check_in ล่าสุดของผู้ใช้จากฐานข้อมูล
    result = await db.execute(
        select(Attendance)
        .where(Attendance.username == attendance_request.username)
        .order_by(Attendance.id.desc())
        .limit(1)  # ดึงข้อมูลเพียงรายการเดียว
    )
    attendance = result.scalars().first()
    
    # ตรวจสอบว่ามีการ check_in ก่อนหน้านี้หรือไม่
    if not attendance:
        raise HTTPException(status_code=404, detail="Check-in not found")

    # แปลง check_out_time เป็น timezone-naive ก่อนบันทึกลงฐานข้อมูล
    check_out_time = (attendance_request.check_out or datetime.now(timezone.utc)).replace(tzinfo=None)

    # แปลง attendance.check_in ให้เป็น timezone-naive
    check_in_time_naive = attendance.check_in.replace(tzinfo=None)

    # ตรวจสอบสถานะการลงเวลา
    status = calculate_attendance_status(attendance.check_in, check_out_time)

    # ตรวจสอบว่า check_out_time น้อยกว่า check_in_time หรือไม่
    if check_out_time <= check_in_time_naive:
        raise HTTPException(status_code=422, detail="Check-out time must be after check-in time")


    # อัปเดตข้อมูล check_out และสถานะ
    attendance.check_out = check_out_time
    attendance.status = status.value

    await db.commit()
    await db.refresh(attendance)

    # แปลงเวลาจาก UTC เป็นเวลาท้องถิ่นก่อนส่งกลับ
    local_check_out_time = convert_utc_to_local(attendance.check_out)

    # แคชข้อมูล check_out ใน Redis
    attendance_data = {
        "check_out_time": local_check_out_time.isoformat(),
        "status": status.value
    }
    redis_client.setex(f"attendance:checkout:{attendance_request.username}", 86400, json.dumps(attendance_data))  # แคชเป็นเวลา 1 วัน

    return {
        "status": "Check-out successful",
        "check_out": local_check_out_time.isoformat(),  # ส่งกลับในรูปแบบ ISO พร้อมเวลาท้องถิ่น
        "attendance_status": status.value
    }


if __name__ == "__main__":
    import uvicorn
    preload_users_to_redis()
    print("Preloaded all users to Redis")
    uvicorn.run(app, host="127.0.0.1", port=2000)
