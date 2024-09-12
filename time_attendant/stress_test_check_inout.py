from locust import HttpUser, TaskSet, task, between
import random
import pandas as pd

# โหลดข้อมูลจากไฟล์ CSV
users_data = pd.read_csv("/Users/seal/Downloads/Unique_Usernames_and_Hashed_Passwords.csv")

# แบ่งผู้ใช้สำหรับ check_in และ check_out
users_for_check_in = users_data.sample(frac=1).to_dict('records')  # สุ่มผู้ใช้ทั้งหมดสำหรับ check_in
users_for_check_out = []  # ลิสต์นี้จะเก็บผู้ใช้ที่ทำ check_in แล้ว เพื่อใช้ในการทำ check_out

class TimeAttendantTaskSet(TaskSet):
    
    def on_start(self):
        """เตรียมข้อมูลผู้ใช้สำหรับ check_in หรือ check_out"""
        global users_for_check_in, users_for_check_out
        
        if users_for_check_in:
            # สุ่มผู้ใช้สำหรับ check_in ที่ยังไม่ถูกใช้
            user_info = users_for_check_in.pop(0)  # ดึงผู้ใช้คนแรกออกจากลิสต์ (pop)
            self.username = str(user_info['Username'])
            self.password = user_info['Password']
            users_for_check_out.append(user_info)  # เพิ่มผู้ใช้ไปยังลิสต์สำหรับ check_out
        elif users_for_check_out:
            # สุ่มผู้ใช้สำหรับ check_out
            user_info = random.choice(users_for_check_out)  # สุ่มเลือกผู้ใช้จากลิสต์ที่ทำ check_in แล้ว
            self.username = str(user_info['Username'])
            self.password = user_info['Password']

    @task(1)
    def check_user_and_check_in(self):
        """ตรวจสอบผู้ใช้และทำการ check_in"""
        if users_for_check_in:
            response = self.client.post("/check_user/", json={"username": self.username, "password": self.password})
            if response.status_code == 200:
                self.check_in()
        else:
            self.check_out()  # เมื่อไม่มีผู้ใช้ในลิสต์ check_in แล้วให้ไปทำ check_out

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
