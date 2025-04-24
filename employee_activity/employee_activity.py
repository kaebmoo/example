import pulp
import numpy as np

# ข้อมูลพนักงานและกิจกรรม (จากตารางของคุณ)
employees = [
    "น.ส. *****จิตร ศรี*****",
    "น.ส. *****ภา สิน*****",
    "น.ส. *****ภา *****ผล",
    "น.ส. *****ศรัณย์ มา*****",
    "น.ส. *****กานต์ เจน*****",
    "น.ส. *****ภา ม*****",
    "น.ส. *****ตา ส*****",
    "น.ส. *****ดา เกษม*****",
    "นาง *****วรรณ ฤกษ์*****",
    "นาย *****ยะ เติม*****",
    "นาย *****กร ชม*****"
]

activities = [
    "Bill Payments",
    "Corporate IT", 
    "CRM Support", 
    "Strategic & Enterprise Planning"
]

# สัดส่วนการทำงานของพนักงานแต่ละคน (จากตาราง)
employee_activities = {
    "น.ส. *****จิตร ศรี*****": {"Bill Payments": 0.2, "Corporate IT": 0.3, "CRM Support": 0.1, "Strategic & Enterprise Planning": 0.4},
    "น.ส. *****ภา สิน*****": {"Bill Payments": 0.1, "Corporate IT": 0.6, "CRM Support": 0.2, "Strategic & Enterprise Planning": 0.1},
    "น.ส. *****ภา *****ผล": {"Bill Payments": 0.0, "Corporate IT": 0.5, "CRM Support": 0.1, "Strategic & Enterprise Planning": 0.4},
    "น.ส. *****ศรัณย์ มา*****": {"Bill Payments": 0.0, "Corporate IT": 0.7, "CRM Support": 0.3, "Strategic & Enterprise Planning": 0.0},
    "น.ส. *****กานต์ เจน*****": {"Bill Payments": 0.0, "Corporate IT": 0.7, "CRM Support": 0.3, "Strategic & Enterprise Planning": 0.0},
    "น.ส. *****ภา ม*****": {"Bill Payments": 0.0, "Corporate IT": 0.7, "CRM Support": 0.3, "Strategic & Enterprise Planning": 0.0},
    "น.ส. *****ตา ส*****": {"Bill Payments": 0.0, "Corporate IT": 1.0, "CRM Support": 0.0, "Strategic & Enterprise Planning": 0.0},
    "น.ส. *****ดา เกษม*****": {"Bill Payments": 0.0, "Corporate IT": 0.7, "CRM Support": 0.3, "Strategic & Enterprise Planning": 0.0},
    "นาง *****วรรณ ฤกษ์*****": {"Bill Payments": 0.0, "Corporate IT": 0.4, "CRM Support": 0.0, "Strategic & Enterprise Planning": 0.6},
    "นาย *****ยะ เติม*****": {"Bill Payments": 0.0, "Corporate IT": 0.6, "CRM Support": 0.4, "Strategic & Enterprise Planning": 0.0},
    "นาย *****กร ชม*****": {"Bill Payments": 0.0, "Corporate IT": 1.0, "CRM Support": 0.0, "Strategic & Enterprise Planning": 0.0}
}

# คำนวณสัดส่วนกิจกรรมในภาพรวม
total_activities = {activity: 0 for activity in activities}
for emp, acts in employee_activities.items():
    for act, value in acts.items():
        total_activities[act] += value

total_sum = sum(total_activities.values())
activity_ratios = {act: val/total_sum for act, val in total_activities.items()}

# คำนวณเป้าหมายจำนวนพนักงานในแต่ละกิจกรรม
num_employees = len(employees)
target_employees = {act: round(num_employees * ratio) for act, ratio in activity_ratios.items()}

# กำหนดเงื่อนไขพิเศษ - พนักงานที่เลือกกิจกรรมเดียวด้วยสัดส่วน 100%
special_assignments = {}
for emp, acts in employee_activities.items():
    if max(acts.values()) == 1.0:
        for act, val in acts.items():
            if val == 1.0:
                special_assignments[emp] = act

# คะแนนของแต่ละการมอบหมาย (70% จากสัดส่วนของพนักงาน, 30% จากสัดส่วนของส่วนงาน)
INDIVIDUAL_WEIGHT = 0.7
SECTION_WEIGHT = 0.3

scores = {}
for emp in employees:
    for act in activities:
        ind_score = employee_activities[emp].get(act, 0) * INDIVIDUAL_WEIGHT
        sec_score = activity_ratios.get(act, 0) * SECTION_WEIGHT
        scores[(emp, act)] = ind_score + sec_score

# สร้างโมเดล
model = pulp.LpProblem("Employee_Assignment", pulp.LpMaximize)

# สร้างตัวแปรตัดสินใจ
x = pulp.LpVariable.dicts("assign", 
                         [(emp, act) for emp in employees for act in activities], 
                         cat='Binary')

# กำหนดฟังก์ชันวัตถุประสงค์
model += pulp.lpSum(scores[(emp, act)] * x[(emp, act)] for emp in employees for act in activities)

# กำหนดข้อจำกัด - พนักงานแต่ละคนได้รับมอบหมายกิจกรรมเดียว
for emp in employees:
    model += pulp.lpSum(x[(emp, act)] for act in activities) == 1

# กำหนดข้อจำกัด - จำนวนพนักงานที่ได้รับมอบหมายกิจกรรมเท่ากับเป้าหมาย
for act in activities:
    model += pulp.lpSum(x[(emp, act)] for emp in employees) == target_employees[act]

# เพิ่มข้อจำกัดสำหรับพนักงานที่มีเงื่อนไขพิเศษ
for emp, act in special_assignments.items():
    model += x[(emp, act)] == 1

# แก้ปัญหา
model.solve()

# แสดงผลลัพธ์
result = {}
for emp in employees:
    for act in activities:
        if pulp.value(x[(emp, act)]) == 1:
            result[emp] = act

print("ผลการมอบหมายกิจกรรม:")
for emp, act in result.items():
    print(f"{emp}: {act} (สัดส่วนเดิม {employee_activities[emp][act]*100:.0f}%)")