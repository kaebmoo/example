from locust import HttpUser, TaskSet, task, between
import random
import pandas as pd

# โหลดข้อมูลจากไฟล์ CSV
users_data = pd.read_csv("/Users/seal/Downloads/Unique_Usernames_and_Hashed_Passwords.csv")

class TimeAttendantTaskSet(TaskSet):
    
    def on_start(self):
        """เตรียมข้อมูลผู้ใช้จากไฟล์ CSV เมื่อเริ่มทดสอบ"""
        user_info = users_data.sample().iloc[0]  # สุ่มเลือกผู้ใช้ 1 คนจากไฟล์ CSV
        self.username = str(user_info['Username'])
        self.password = user_info['Password']

    @task(1)
    def check_user(self):
        """ตรวจสอบผู้ใช้"""
        response = self.client.post("/check_user/", json={"username": self.username, "password": self.password})
        if response.status_code == 200:
            self.check_in()

    def check_in(self):
        """จำลองการลงเวลาเข้างาน"""
        data = {
            "username": self.username,
            "password": self.password,
            "check_in": None  # ให้ระบบใช้เวลาปัจจุบัน
        }
        self.client.post("/check_in/", json=data)

    @task(2)
    def check_out(self):
        """จำลองการลงเวลาออกงาน"""
        data = {
            "username": self.username,
            "password": self.password,
            "check_out": None  # ให้ระบบใช้เวลาปัจจุบัน
        }
        self.client.post("/check_out/", json=data)

class TimeAttendantUser(HttpUser):
    tasks = [TimeAttendantTaskSet]
    wait_time = between(1, 5)  # รอเวลา 1 ถึง 5 วินาทีระหว่างการทดสอบแต่ละ task
