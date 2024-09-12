from datetime import datetime, timedelta
from enum import Enum

class AttendanceStatus(Enum):
    NORMAL = "ปกติ"
    LATE = "สาย"
    EARLY_LEAVE = "ออกก่อน"

class TimeAttendanceSystem:
    def __init__(self, day_shift_start="08:30", day_shift_end="16:30"):
        self.attendance_records = {}
        self.day_shift_start = datetime.strptime(day_shift_start, "%H:%M").time()
        self.day_shift_end = datetime.strptime(day_shift_end, "%H:%M").time()

    def check_in(self, employee_id: str, check_in_time: datetime, is_retroactive: bool = False):
        today = check_in_time.date()
        if employee_id in self.attendance_records and today in self.attendance_records[employee_id]:
            return False, "พนักงานได้ลงเวลาเข้างานในวันนี้แล้ว"
        
        if is_retroactive and not self._approve_retroactive_entry():
            return False, "การลงเวลาย้อนหลังไม่ได้รับการอนุมัติ"

        status = AttendanceStatus.NORMAL
        if check_in_time.time() > self.day_shift_start:
            status = AttendanceStatus.LATE

        if employee_id not in self.attendance_records:
            self.attendance_records[employee_id] = {}
        self.attendance_records[employee_id][today] = {"check_in": check_in_time, "status": status}
        
        return True, f"ลงเวลาเข้างานสำเร็จ สถานะ: {status.value}"

    def check_out(self, employee_id: str, check_out_time: datetime, is_retroactive: bool = False):
        today = check_out_time.date()

        if employee_id not in self.attendance_records:
            return False, "ไม่พบข้อมูลการลงเวลาเข้างานของพนักงาน"

        if today not in self.attendance_records[employee_id]:
            return False, "ไม่พบข้อมูลการลงเวลาเข้างานของพนักงานสำหรับวันนี้"

        if is_retroactive and not self._approve_retroactive_entry():
            return False, "การลงเวลาย้อนหลังไม่ได้รับการอนุมัติ"

        check_in_time = self.attendance_records[employee_id][today]["check_in"]

        if check_out_time <= check_in_time:
            return False, "เวลาออกงานต้องมาหลังเวลาเข้างาน"

        work_duration = check_out_time - check_in_time
        status = self.attendance_records[employee_id][today]["status"]

        expected_end_time = datetime.combine(check_out_time.date(), self.day_shift_end)
        
        # ตรวจสอบสถานะ Early Leave สำหรับกะกลางวัน
        if check_out_time.time() < self.day_shift_end and work_duration < timedelta(hours=8):
            status = AttendanceStatus.EARLY_LEAVE
        else:
            status = AttendanceStatus.NORMAL

        self.attendance_records[employee_id][today]["check_out"] = check_out_time
        self.attendance_records[employee_id][today]["status"] = status

        return True, f"ลงเวลาออกงานสำเร็จ สถานะ: {status.value}"

    def _approve_retroactive_entry(self):
        return True

# ตัวอย่างการใช้งาน
system = TimeAttendanceSystem()

# กะกลางวัน (08:30 - 16:30)
print("กะกลางวัน:")
success, message = system.check_in("EMP001", datetime(2024, 9, 12, 8, 22))
print(message)
success, message = system.check_out("EMP001", datetime(2024, 9, 12, 16, 30))
print(message)

success, message = system.check_in("EMP002", datetime(2024, 9, 12, 9, 0))
print(message)
success, message = system.check_out("EMP002", datetime(2024, 9, 12, 16, 0))
print(message)

success, message = system.check_in("EMP002", datetime(2024, 9, 12, 9, 0))
print(message)
success, message = system.check_out("EMP002", datetime(2024, 9, 12, 17, 0))
print(message)