from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, exists
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, relationship
import os
import pytz

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

# ดึงค่าจากไฟล์ .env
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# กำหนดค่าฐานข้อมูล
DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

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

# Dependency สำหรับสร้าง session
async def get_db():
    """Dependency สำหรับสร้าง session"""
    async with SessionLocal() as session:
        yield session

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
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
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
    
    # ดึงข้อมูล check_in ของผู้ใช้ในวันนี้
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
        raise HTTPException(status_code=400, detail="Already checked in today")

    # บันทึกเวลา check_in
    check_in_time = (attendance_request.check_in or datetime.now(timezone.utc)).replace(tzinfo=None)

    status = calculate_attendance_status(check_in_time)

    new_attendance = Attendance(username=user.username, check_in=check_in_time, status=status.value)
    db.add(new_attendance)
    await db.commit()
    await db.refresh(new_attendance)
    
    # แปลงเวลาเป็นเวลาท้องถิ่นก่อนส่งกลับ
    local_check_in_time = convert_utc_to_local(new_attendance.check_in)
    
    return {
        "status": "Check-in successful",
        "check_in": local_check_in_time.isoformat(),  # ส่งกลับในรูปแบบ ISO และแสดงเวลาท้องถิ่น
        "attendance_status": status.value
    }

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
    
    # ดึงข้อมูลการ check_in ล่าสุดของผู้ใช้
    result = await db.execute(
        select(Attendance)
        .where(Attendance.username == attendance_request.username)
        .order_by(Attendance.id.desc())
        .limit(1)  # ดึงข้อมูลเพียงรายการเดียว
    )
    attendance = result.scalars().first()
    
    # ตรวจสอบว่ามีการ check_in ก่อนหน้านี้หรือไม่
    if not attendance:
        raise HTTPException(status_code=400, detail="Check-in not found")

    # แปลง check_out_time เป็น timezone-naive ก่อนบันทึกลงฐานข้อมูล
    check_out_time = (attendance_request.check_out or datetime.now(timezone.utc)).replace(tzinfo=None)

    # แปลง attendance.check_in ให้เป็น timezone-naive
    check_in_time_naive = attendance.check_in.replace(tzinfo=None)

    # ตรวจสอบสถานะการลงเวลา
    status = calculate_attendance_status(attendance.check_in, check_out_time)

    # ตรวจสอบว่า check_out_time น้อยกว่า check_in_time หรือไม่
    if check_out_time <= check_in_time_naive:
        raise HTTPException(status_code=400, detail="Check-out time must be after check-in time")

    # อัปเดตข้อมูล check_out และสถานะ
    attendance.check_out = check_out_time
    attendance.status = status.value

    await db.commit()
    await db.refresh(attendance)

    # แปลงเวลาจาก UTC เป็นเวลาท้องถิ่นก่อนส่งกลับ
    local_check_out_time = convert_utc_to_local(attendance.check_out)

    return {
        "status": "Check-out successful",
        "check_out": local_check_out_time.isoformat(),  # ส่งกลับในรูปแบบ ISO พร้อมเวลาท้องถิ่น
        "attendance_status": status.value
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=2000)
