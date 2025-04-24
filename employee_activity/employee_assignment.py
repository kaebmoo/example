import pandas as pd
import pulp
import numpy as np
import os

# อ่านข้อมูลจากไฟล์ CSV และคำนวณแยกตามส่วนงาน
def assign_activities_by_section(input_file, output_dir, individual_weight=0.7, section_weight=0.3):
    """
    คำนวณการมอบหมายกิจกรรมแยกตามส่วนงาน
    
    Parameters:
    -----------
    input_file : str
        ชื่อไฟล์ข้อมูลนำเข้า (CSV)
    output_dir : str
        ชื่อโฟลเดอร์ที่จะเก็บผลลัพธ์
    individual_weight : float
        น้ำหนักของสัดส่วนงานของพนักงาน (ค่าเริ่มต้น: 0.7)
    section_weight : float
        น้ำหนักของสัดส่วนภาพรวมของส่วนงาน (ค่าเริ่มต้น: 0.3)
    
    Returns:
    --------
    dict
        ข้อมูลสรุปผลการคำนวณของทุกส่วนงาน
    """
    # อ่านข้อมูลจาก CSV file
    df = pd.read_csv(input_file)
    
    # สร้างโฟลเดอร์สำหรับเก็บผลลัพธ์ถ้ายังไม่มี
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # แบ่งข้อมูลตามส่วนงาน
    sections = df['SECTION_NAME'].unique()
    print(f"พบส่วนงานทั้งหมด {len(sections)} ส่วนงาน")
    
    # เก็บผลลัพธ์รวมของทุกส่วนงาน
    all_results = {}
    
    # ประมวลผลแต่ละส่วนงานแยกกัน
    for section in sections:
        print(f"\n{'='*50}")
        print(f"กำลังประมวลผลส่วนงาน: {section}")
        print(f"{'='*50}")
        
        # กรองข้อมูลเฉพาะส่วนงานนี้
        section_df = df[df['SECTION_NAME'] == section].copy()
        
        # สร้างชื่อไฟล์ผลลัพธ์สำหรับส่วนงานนี้
        section_safe_name = section.replace("/", "_").replace("\\", "_")
        section_output_file = os.path.join(output_dir, f"{section_safe_name}_assignments.csv")
        
        # เรียกใช้ฟังก์ชันคำนวณสำหรับแต่ละส่วนงาน
        results = assign_single_activity_from_df(
            section_df, 
            section_output_file, 
            section_name=section,
            individual_weight=individual_weight, 
            section_weight=section_weight
        )
        
        # เก็บผลลัพธ์ไว้ในตัวแปรรวม
        all_results[section] = results
    
    # สร้างสรุปผลรวมทั้งหมด
    create_overall_summary(all_results, output_dir)
    
    return all_results

def assign_single_activity_from_df(df, output_file, section_name=None, individual_weight=0.7, section_weight=0.3):
    """
    คำนวณการมอบหมายกิจกรรมให้พนักงานจาก DataFrame
    
    Parameters:
    -----------
    df : pandas.DataFrame
        ข้อมูลการทำงานของพนักงาน
    output_file : str
        ชื่อไฟล์ผลลัพธ์
    section_name : str, optional
        ชื่อส่วนงาน (สำหรับแสดงในรายงาน)
    individual_weight : float
        น้ำหนักของสัดส่วนงานของพนักงาน
    section_weight : float
        น้ำหนักของสัดส่วนภาพรวมของส่วนงาน
    
    Returns:
    --------
    tuple
        (result_df, activity_df, summary_df) ข้อมูลผลลัพธ์
    """
    # ดึงข้อมูลพนักงานและกิจกรรมทั้งหมด
    employees = df['EMPLOYEE_ID'].unique().tolist()
    employee_names = df.groupby('EMPLOYEE_ID')['NAME'].first().to_dict()
    activities = df['Activity'].unique().tolist()
    
    # ตรวจสอบจำนวนพนักงานและกิจกรรม
    if len(employees) == 0:
        print(f"ไม่พบข้อมูลพนักงานในส่วนงาน {section_name}")
        return None
    
    if len(activities) == 0:
        print(f"ไม่พบข้อมูลกิจกรรมในส่วนงาน {section_name}")
        return None
    
    # สร้าง dictionary ของสัดส่วนกิจกรรมของแต่ละพนักงาน
    employee_activities = {}
    for emp_id in employees:
        emp_df = df[df['EMPLOYEE_ID'] == emp_id]
        emp_name = emp_df['NAME'].iloc[0]
        
        # สร้าง dictionary ของกิจกรรมและสัดส่วนสำหรับพนักงานคนนี้
        activities_dict = {row['Activity']: row['Values'] for _, row in emp_df.iterrows()}
        
        # เติมกิจกรรมที่พนักงานไม่ได้ทำด้วยค่า 0
        for act in activities:
            if act not in activities_dict:
                activities_dict[act] = 0.0
                
        employee_activities[emp_id] = {
            'name': emp_name,
            'activities': activities_dict
        }
    
    # คำนวณสัดส่วนกิจกรรมในภาพรวมของส่วนงาน
    total_activities = {activity: 0 for activity in activities}
    for emp_id, emp_data in employee_activities.items():
        for act, value in emp_data['activities'].items():
            total_activities[act] += value
    
    total_sum = sum(total_activities.values())
    activity_ratios = {act: val/total_sum for act, val in total_activities.items()}
    
    # คำนวณเป้าหมายจำนวนพนักงานในแต่ละกิจกรรม
    num_employees = len(employees)
    target_employees = {act: round(num_employees * ratio) for act, ratio in activity_ratios.items()}
    
    section_info = f"ส่วนงาน: {section_name}" if section_name else ""
    print(f"{section_info} - จำนวนพนักงานทั้งหมด: {num_employees} คน")
    print(f"{section_info} - เป้าหมายจำนวนพนักงานในแต่ละกิจกรรม: {target_employees}")
    
    # กำหนดเงื่อนไขพิเศษ - พนักงานที่เลือกกิจกรรมเดียวด้วยสัดส่วน 100%
    special_assignments = {}
    for emp_id, emp_data in employee_activities.items():
        max_val = max(emp_data['activities'].values())
        if max_val == 1.0:
            for act, val in emp_data['activities'].items():
                if val == 1.0:
                    special_assignments[emp_id] = act
                    print(f"{section_info} - พนักงานพิเศษ: {emp_data['name']} ({emp_id}) ต้องทำกิจกรรม {act}")
    
    # คะแนนของแต่ละการมอบหมาย
    scores = {}
    for emp_id in employees:
        for act in activities:
            ind_score = employee_activities[emp_id]['activities'].get(act, 0) * individual_weight
            sec_score = activity_ratios.get(act, 0) * section_weight
            scores[(emp_id, act)] = ind_score + sec_score
    
    # สร้างโมเดล
    model = pulp.LpProblem("Employee_Assignment", pulp.LpMaximize)
    
    # สร้างตัวแปรตัดสินใจ
    x = pulp.LpVariable.dicts("assign", 
                             [(emp_id, act) for emp_id in employees for act in activities], 
                             cat='Binary')
    
    # กำหนดฟังก์ชันวัตถุประสงค์
    model += pulp.lpSum(scores[(emp_id, act)] * x[(emp_id, act)] for emp_id in employees for act in activities)
    
    # กำหนดข้อจำกัด - พนักงานแต่ละคนได้รับมอบหมายกิจกรรมเดียว
    for emp_id in employees:
        model += pulp.lpSum(x[(emp_id, act)] for act in activities) == 1
    
    # ตรวจสอบว่าจำนวนพนักงานทั้งหมดพอดีกับผลรวมของเป้าหมาย
    total_target = sum(target_employees.values())
    if total_target != num_employees:
        print(f"{section_info} - คำเตือน: จำนวนพนักงานทั้งหมด ({num_employees}) ไม่เท่ากับผลรวมของเป้าหมาย ({total_target})")
        
        # ปรับเป้าหมายให้รวมเท่ากับจำนวนพนักงานทั้งหมด
        diff = num_employees - total_target
        if diff > 0:
            # ถ้ามีพนักงานมากเกินไป เพิ่มเป้าหมายให้กับกิจกรรมที่มีสัดส่วนมากที่สุด
            sorted_acts = sorted(activity_ratios.items(), key=lambda x: x[1], reverse=True)
            target_employees[sorted_acts[0][0]] += diff
        else:
            # ถ้ามีพนักงานน้อยเกินไป ลดเป้าหมายจากกิจกรรมที่มีสัดส่วนน้อยที่สุด
            sorted_acts = sorted(activity_ratios.items(), key=lambda x: x[1])
            for i in range(len(sorted_acts)):
                act = sorted_acts[i][0]
                if target_employees[act] >= abs(diff):
                    target_employees[act] += diff  # diff เป็นลบอยู่แล้ว
                    break
                else:
                    diff += target_employees[act]  # เพิ่มค่าเข้าไป (diff < 0)
                    target_employees[act] = 0
        
        print(f"{section_info} - เป้าหมายจำนวนพนักงานที่ปรับแล้ว: {target_employees}")
    
    # กำหนดข้อจำกัด - จำนวนพนักงานที่ได้รับมอบหมายกิจกรรมเท่ากับเป้าหมาย
    for act in activities:
        if target_employees[act] > 0:  # เฉพาะกิจกรรมที่ต้องการพนักงาน
            model += pulp.lpSum(x[(emp_id, act)] for emp_id in employees) == target_employees[act]
    
    # เพิ่มข้อจำกัดสำหรับพนักงานที่มีเงื่อนไขพิเศษ
    for emp_id, act in special_assignments.items():
        model += x[(emp_id, act)] == 1
    
    # แก้ปัญหา
    solver_status = model.solve()
    
    # ตรวจสอบว่าแก้ปัญหาสำเร็จหรือไม่
    if solver_status != pulp.LpStatusOptimal:
        print(f"{section_info} - ไม่สามารถหาคำตอบที่เหมาะสมได้ สถานะ: {pulp.LpStatus[solver_status]}")
        
        # ถ้าแก้ปัญหาไม่สำเร็จ ใช้วิธี greedy algorithm แทน
        return use_greedy_algorithm(employee_activities, activities, activity_ratios, 
                                   special_assignments, output_file, individual_weight, section_weight,
                                   section_name=section_name)
    
    # รวบรวมผลลัพธ์
    results = []
    for emp_id in employees:
        emp_data = employee_activities[emp_id]
        assigned_activity = None
        
        for act in activities:
            if pulp.value(x[(emp_id, act)]) == 1:
                assigned_activity = act
                break
        
        if assigned_activity:
            original_value = emp_data['activities'].get(assigned_activity, 0)
            score = scores.get((emp_id, assigned_activity), 0)
            
            results.append({
                'COST_CENTER': df[df['EMPLOYEE_ID'] == emp_id]['COST_CENTER'].iloc[0],
                'SECTION_NAME': section_name if section_name else df[df['EMPLOYEE_ID'] == emp_id]['SECTION_NAME'].iloc[0],
                'EMPLOYEE_ID': emp_id,
                'NAME': emp_data['name'],
                'ASSIGNED_ACTIVITY': assigned_activity,
                'ORIGINAL_VALUE': original_value,
                'SCORE': score
            })
    
    # สร้าง DataFrame จากผลลัพธ์และบันทึกลงไฟล์ CSV
    result_df = pd.DataFrame(results)
    
    # สร้าง DataFrame เพิ่มเติมเพื่อแสดงรายละเอียดกิจกรรมเดิมของพนักงาน
    activity_details = []
    for emp_id in employees:
        emp_data = employee_activities[emp_id]
        
        # หากิจกรรมที่ได้รับมอบหมาย
        assigned = next((r['ASSIGNED_ACTIVITY'] for r in results if r['EMPLOYEE_ID'] == emp_id), None)
        
        # สร้างข้อความรายละเอียดกิจกรรมเดิม
        activity_str = ", ".join([f"{act} ({val*100:.0f}%)" for act, val in emp_data['activities'].items() if val > 0])
        
        activity_details.append({
            'COST_CENTER': df[df['EMPLOYEE_ID'] == emp_id]['COST_CENTER'].iloc[0],
            'SECTION_NAME': section_name if section_name else df[df['EMPLOYEE_ID'] == emp_id]['SECTION_NAME'].iloc[0],
            'EMPLOYEE_ID': emp_id,
            'NAME': emp_data['name'],
            'ORIGINAL_ACTIVITIES': activity_str,
            'ASSIGNED_ACTIVITY': assigned
        })
    
    activity_df = pd.DataFrame(activity_details)
    
    # สรุปจำนวนพนักงานในแต่ละกิจกรรม
    assigned_counts = {act: 0 for act in activities}
    for r in results:
        act = r['ASSIGNED_ACTIVITY']
        assigned_counts[act] = assigned_counts.get(act, 0) + 1
    
    summary = []
    for act in activities:
        count = assigned_counts.get(act, 0)
        target = target_employees.get(act, 0)
        ratio = activity_ratios.get(act, 0)
        
        summary.append({
            'ACTIVITY': act,
            'ASSIGNED_COUNT': count,
            'TARGET_COUNT': target,
            'SECTION_RATIO': ratio,
            'MATCHING': count == target
        })
    
    summary_df = pd.DataFrame(summary)
    
    # คำนวณความตรงกับกิจกรรมที่พนักงานทำมากที่สุด
    match_count = 0
    for emp_id in employees:
        emp_data = employee_activities[emp_id]
        # หากิจกรรมที่มีสัดส่วนมากที่สุด
        if any(emp_data['activities'].values()):  # ตรวจสอบว่ามีกิจกรรมหรือไม่
            max_act = max(emp_data['activities'].items(), key=lambda x: x[1])[0]
            # หากิจกรรมที่ได้รับมอบหมาย
            assigned = next((r['ASSIGNED_ACTIVITY'] for r in results if r['EMPLOYEE_ID'] == emp_id), None)
            
            if max_act == assigned:
                match_count += 1
    
    match_percent = (match_count / num_employees) * 100 if num_employees > 0 else 0
    print(f"{section_info} - พนักงานที่ได้รับมอบหมายตรงกับกิจกรรมที่ทำมากที่สุด: {match_count}/{num_employees} ({match_percent:.2f}%)")
    
    # บันทึกข้อมูลลงไฟล์ CSV
    result_df.to_csv(output_file, index=False)
    activity_df.to_csv(output_file.replace('.csv', '_details.csv'), index=False)
    summary_df.to_csv(output_file.replace('.csv', '_summary.csv'), index=False)
    
    print(f"{section_info} - บันทึกผลลัพธ์ลงไฟล์ {output_file} และไฟล์เพิ่มเติมเรียบร้อยแล้ว")
    
    return result_df, activity_df, summary_df

# ฟังก์ชันใช้วิธี greedy algorithm ในกรณีที่ linear programming ไม่สามารถหาคำตอบได้
def use_greedy_algorithm(employee_activities, activities, activity_ratios, special_assignments, output_file,
                         individual_weight=0.7, section_weight=0.3, section_name=None):
    section_info = f"ส่วนงาน: {section_name}" if section_name else ""
    print(f"{section_info} - ใช้วิธี Greedy Algorithm แทน")
    
    employees = list(employee_activities.keys())
    num_employees = len(employees)
    
    # คำนวณเป้าหมายจำนวนพนักงานในแต่ละกิจกรรม
    target_employees = {act: round(num_employees * ratio) for act, ratio in activity_ratios.items()}
    
    # คำนวณคะแนนสำหรับแต่ละการมอบหมาย
    scores = {}
    for emp_id, emp_data in employee_activities.items():
        scores[emp_id] = {}
        for act in activities:
            ind_score = emp_data['activities'].get(act, 0) * individual_weight
            sec_score = activity_ratios.get(act, 0) * section_weight
            scores[emp_id][act] = ind_score + sec_score
    
    # มอบหมายกิจกรรมให้กับพนักงานที่มีเงื่อนไขพิเศษก่อน
    assigned_employees = set()
    assigned_activities = {act: 0 for act in activities}
    assignments = {}
    
    for emp_id, act in special_assignments.items():
        assignments[emp_id] = act
        assigned_employees.add(emp_id)
        assigned_activities[act] += 1
    
    # สร้าง priority queue ของทุกการมอบหมายที่เป็นไปได้
    all_assignments = []
    for emp_id in employees:
        if emp_id not in assigned_employees:  # เฉพาะพนักงานที่ยังไม่ได้รับมอบหมาย
            for act in activities:
                all_assignments.append({
                    'emp_id': emp_id,
                    'activity': act,
                    'score': scores[emp_id][act]
                })
    
    # เรียงลำดับตามคะแนน (จากมากไปน้อย)
    all_assignments.sort(key=lambda x: x['score'], reverse=True)
    
    # มอบหมายกิจกรรมให้กับพนักงานที่เหลือ
    for assignment in all_assignments:
        emp_id = assignment['emp_id']
        act = assignment['activity']
        
        if emp_id in assigned_employees:
            continue  # พนักงานคนนี้ได้รับมอบหมายแล้ว
        
        # ตรวจสอบว่ากิจกรรมนี้ยังต้องการพนักงานเพิ่มหรือไม่
        if assigned_activities[act] < target_employees[act]:
            assignments[emp_id] = act
            assigned_employees.add(emp_id)
            assigned_activities[act] += 1
    
    # หากยังมีพนักงานที่ไม่ได้รับมอบหมาย ให้มอบหมายตามคะแนนสูงสุด
    for emp_id in employees:
        if emp_id not in assigned_employees:
            # หากิจกรรมที่มีคะแนนสูงสุดสำหรับพนักงานคนนี้
            best_act = max(scores[emp_id].items(), key=lambda x: x[1])[0]
            assignments[emp_id] = best_act
            assigned_activities[best_act] += 1
    
    # สร้างผลลัพธ์
    results = []
    for emp_id, act in assignments.items():
        emp_data = employee_activities[emp_id]
        original_value = emp_data['activities'].get(act, 0)
        score = scores[emp_id][act]
        
        results.append({
            'EMPLOYEE_ID': emp_id,
            'NAME': emp_data['name'],
            'ASSIGNED_ACTIVITY': act,
            'ORIGINAL_VALUE': original_value,
            'SCORE': score
        })
    
    # สร้าง DataFrame และบันทึกลงไฟล์ CSV (เหมือนฟังก์ชันหลัก)
    result_df = pd.DataFrame(results)
    
    # สร้าง DataFrame เพิ่มเติม (เหมือนฟังก์ชันหลัก)
    activity_details = []
    for emp_id in employees:
        emp_data = employee_activities[emp_id]
        assigned = assignments.get(emp_id)
        
        activity_str = ", ".join([f"{act} ({val*100:.0f}%)" for act, val in emp_data['activities'].items() if val > 0])
        
        activity_details.append({
            'EMPLOYEE_ID': emp_id,
            'NAME': emp_data['name'],
            'ORIGINAL_ACTIVITIES': activity_str,
            'ASSIGNED_ACTIVITY': assigned
        })
    
    activity_df = pd.DataFrame(activity_details)
    
    # สรุปจำนวนพนักงานในแต่ละกิจกรรม
    summary = []
    for act in activities:
        count = assigned_activities.get(act, 0)
        target = target_employees.get(act, 0)
        ratio = activity_ratios.get(act, 0)
        
        summary.append({
            'ACTIVITY': act,
            'ASSIGNED_COUNT': count,
            'TARGET_COUNT': target,
            'SECTION_RATIO': ratio,
            'MATCHING': count == target
        })
    
    summary_df = pd.DataFrame(summary)
    
    # บันทึกข้อมูลลงไฟล์ CSV
    result_df.to_csv(output_file, index=False)
    activity_df.to_csv(output_file.replace('.csv', '_details.csv'), index=False)
    summary_df.to_csv(output_file.replace('.csv', '_summary.csv'), index=False)
    
    print(f"{section_info} - บันทึกผลลัพธ์ลงไฟล์ {output_file} และไฟล์เพิ่มเติมเรียบร้อยแล้ว")
    
    return result_df, activity_df, summary_df

def create_overall_summary(all_results, output_dir):
    """
    สร้างสรุปผลรวมของทุกส่วนงาน
    
    Parameters:
    -----------
    all_results : dict
        ผลลัพธ์ของทุกส่วนงาน
    output_dir : str
        โฟลเดอร์ที่จะเก็บไฟล์สรุป
    """
    # รวมข้อมูลจากทุกส่วนงาน
    all_assignments = []
    all_details = []
    all_summary = []
    
    for section, results in all_results.items():
        if results is None:
            continue
            
        result_df, activity_df, summary_df = results
        
        if result_df is not None:
            all_assignments.append(result_df)
        
        if activity_df is not None:
            all_details.append(activity_df)
            
        if summary_df is not None:
            # เพิ่มชื่อส่วนงานในข้อมูลสรุป
            summary_df = summary_df.copy()
            summary_df['SECTION_NAME'] = section
            all_summary.append(summary_df)
    
    # รวมข้อมูลเป็น DataFrame เดียว
    if all_assignments:
        combined_assignments = pd.concat(all_assignments, ignore_index=True)
        combined_assignments.to_csv(os.path.join(output_dir, "all_assignments.csv"), index=False)
        
    if all_details:
        combined_details = pd.concat(all_details, ignore_index=True)
        combined_details.to_csv(os.path.join(output_dir, "all_details.csv"), index=False)
        
    if all_summary:
        combined_summary = pd.concat(all_summary, ignore_index=True)
        combined_summary.to_csv(os.path.join(output_dir, "all_summary.csv"), index=False)
    
    print(f"\nสรุปผลรวมทั้งหมดได้ถูกบันทึกไว้ในโฟลเดอร์ {output_dir}")


# ฟังก์ชันใช้วิธี greedy algorithm ในกรณีที่ linear programming ไม่สามารถหาคำตอบได้
def use_greedy_algorithm(employee_activities, activities, activity_ratios, special_assignments, output_file,
                         individual_weight=0.7, section_weight=0.3):
    print("ใช้วิธี Greedy Algorithm แทน")
    
    employees = list(employee_activities.keys())
    num_employees = len(employees)
    
    # คำนวณเป้าหมายจำนวนพนักงานในแต่ละกิจกรรม
    target_employees = {act: round(num_employees * ratio) for act, ratio in activity_ratios.items()}
    
    # คำนวณคะแนนสำหรับแต่ละการมอบหมาย
    scores = {}
    for emp_id, emp_data in employee_activities.items():
        scores[emp_id] = {}
        for act in activities:
            ind_score = emp_data['activities'].get(act, 0) * individual_weight
            sec_score = activity_ratios.get(act, 0) * section_weight
            scores[emp_id][act] = ind_score + sec_score
    
    # มอบหมายกิจกรรมให้กับพนักงานที่มีเงื่อนไขพิเศษก่อน
    assigned_employees = set()
    assigned_activities = {act: 0 for act in activities}
    assignments = {}
    
    for emp_id, act in special_assignments.items():
        assignments[emp_id] = act
        assigned_employees.add(emp_id)
        assigned_activities[act] += 1
    
    # สร้าง priority queue ของทุกการมอบหมายที่เป็นไปได้
    all_assignments = []
    for emp_id in employees:
        if emp_id not in assigned_employees:  # เฉพาะพนักงานที่ยังไม่ได้รับมอบหมาย
            for act in activities:
                all_assignments.append({
                    'emp_id': emp_id,
                    'activity': act,
                    'score': scores[emp_id][act]
                })
    
    # เรียงลำดับตามคะแนน (จากมากไปน้อย)
    all_assignments.sort(key=lambda x: x['score'], reverse=True)
    
    # มอบหมายกิจกรรมให้กับพนักงานที่เหลือ
    for assignment in all_assignments:
        emp_id = assignment['emp_id']
        act = assignment['activity']
        
        if emp_id in assigned_employees:
            continue  # พนักงานคนนี้ได้รับมอบหมายแล้ว
        
        # ตรวจสอบว่ากิจกรรมนี้ยังต้องการพนักงานเพิ่มหรือไม่
        if assigned_activities[act] < target_employees[act]:
            assignments[emp_id] = act
            assigned_employees.add(emp_id)
            assigned_activities[act] += 1
    
    # หากยังมีพนักงานที่ไม่ได้รับมอบหมาย ให้มอบหมายตามคะแนนสูงสุด
    for emp_id in employees:
        if emp_id not in assigned_employees:
            # หากิจกรรมที่มีคะแนนสูงสุดสำหรับพนักงานคนนี้
            best_act = max(scores[emp_id].items(), key=lambda x: x[1])[0]
            assignments[emp_id] = best_act
            assigned_activities[best_act] += 1
    
    # สร้างผลลัพธ์
    results = []
    for emp_id, act in assignments.items():
        emp_data = employee_activities[emp_id]
        original_value = emp_data['activities'].get(act, 0)
        score = scores[emp_id][act]
        
        results.append({
            'EMPLOYEE_ID': emp_id,
            'NAME': emp_data['name'],
            'ASSIGNED_ACTIVITY': act,
            'ORIGINAL_VALUE': original_value,
            'SCORE': score
        })
    
    # สร้าง DataFrame และบันทึกลงไฟล์ CSV (เหมือนฟังก์ชันหลัก)
    result_df = pd.DataFrame(results)
    
    # สร้าง DataFrame เพิ่มเติม (เหมือนฟังก์ชันหลัก)
    activity_details = []
    for emp_id in employees:
        emp_data = employee_activities[emp_id]
        assigned = assignments.get(emp_id)
        
        activity_str = ", ".join([f"{act} ({val*100:.0f}%)" for act, val in emp_data['activities'].items() if val > 0])
        
        activity_details.append({
            'EMPLOYEE_ID': emp_id,
            'NAME': emp_data['name'],
            'ORIGINAL_ACTIVITIES': activity_str,
            'ASSIGNED_ACTIVITY': assigned
        })
    
    activity_df = pd.DataFrame(activity_details)
    
    # สรุปจำนวนพนักงานในแต่ละกิจกรรม
    assigned_counts = {act: 0 for act in activities}
    for _, act in assignments.items():
        assigned_counts[act] = assigned_counts.get(act, 0) + 1
    
    summary = []
    for act in activities:
        count = assigned_counts.get(act, 0)
        target = target_employees.get(act, 0)
        ratio = activity_ratios.get(act, 0)
        
        summary.append({
            'ACTIVITY': act,
            'ASSIGNED_COUNT': count,
            'TARGET_COUNT': target,
            'SECTION_RATIO': ratio,
            'MATCHING': count == target
        })
    
    summary_df = pd.DataFrame(summary)
    
    # บันทึกข้อมูลลงไฟล์ CSV
    result_df.to_csv(output_file, index=False)
    activity_df.to_csv(output_file.replace('.csv', '_details.csv'), index=False)
    summary_df.to_csv(output_file.replace('.csv', '_summary.csv'), index=False)
    
    print(f"บันทึกผลลัพธ์ลงไฟล์ {output_file}, {output_file.replace('.csv', '_details.csv')} และ {output_file.replace('.csv', '_summary.csv')} เรียบร้อยแล้ว")
    
    return result_df, activity_df, summary_df

'''
# สามารถรันโค้ดนี้โดยเรียกใช้ฟังก์ชัน assign_single_activity_from_csv
if __name__ == "__main__":
    # กำหนดค่าน้ำหนักในการคำนวณตามต้องการ
    INDIVIDUAL_WEIGHT = 0.7  # น้ำหนักของสัดส่วนงานของพนักงาน
    SECTION_WEIGHT = 0.3     # น้ำหนักของสัดส่วนภาพรวมของส่วนงาน
    
    # เรียกใช้ฟังก์ชัน
    assign_single_activity_from_csv(
        input_file="employee_activities.csv",     # ไฟล์ข้อมูลนำเข้า
        output_file="employee_assignments.csv",   # ไฟล์ผลลัพธ์
        individual_weight=INDIVIDUAL_WEIGHT,
        section_weight=SECTION_WEIGHT
    )
'''

# สามารถรันโค้ดนี้โดยเรียกใช้ฟังก์ชัน assign_activities_by_section
if __name__ == "__main__":
    # กำหนดค่าน้ำหนักในการคำนวณตามต้องการ
    INDIVIDUAL_WEIGHT = 0.7  # น้ำหนักของสัดส่วนงานของพนักงาน
    SECTION_WEIGHT = 0.3     # น้ำหนักของสัดส่วนภาพรวมของส่วนงาน
    
    # เรียกใช้ฟังก์ชันหลัก
    assign_activities_by_section(
        input_file='/Users/seal/Documents/ฝ่ายระบบบริการลูกค้า 1 (ลทท.).csv',     # ไฟล์ข้อมูลนำเข้า
        output_dir="results",                     # โฟลเดอร์ที่จะเก็บผลลัพธ์
        individual_weight=INDIVIDUAL_WEIGHT,
        section_weight=SECTION_WEIGHT
    )