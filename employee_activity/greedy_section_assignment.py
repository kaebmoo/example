#!/usr/bin/env python3
"""
greedy_section_assignment.py

จัดสรรกิจกรรมให้พนักงานแต่ละคน โดยใช้ Greedy + Section-aware Quota
- ล็อกพนักงานที่เลือกกิจกรรมเดียว 100%
- จัดสรรตามคะแนน Values ของแต่ละคน (มากไปน้อย) แต่ไม่เกิน quota ของแต่ละ SECTION
- ปรับ quota ให้ sum == จำนวนพนักงานจริงของแต่ละ SECTION
- มี fallback สำหรับพนักงานที่เหลือ
- รองรับ CLI ด้วย argparse และ logging

*** ไม่ใช่วิธีที่ดีที่สุด

"""

import argparse
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    """
    โหลดข้อมูลจาก CSV
    คาดว่าไฟล์มีคอลัมน์: EMPLOYEE_ID, NAME, SECTION_NAME, Activity, Values
    """
    df = pd.read_csv(csv_path)
    assert {'EMPLOYEE_ID', 'NAME', 'SECTION_NAME', 'Activity', 'Values'}.issubset(df.columns), \
        "CSV ต้องมีคอลัมน์ EMPLOYEE_ID, NAME, SECTION_NAME, Activity, Values"
    return df


def compute_section_quota(
    df: pd.DataFrame
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Dict[str, float]]]:
    """
    คำนวณ quota ของแต่ละ SECTION และเก็บ target ratio
    คืนค่า:
      section_quota: { section_name: { activity: quota_count } }
      section_target: { section_name: { activity: target_ratio } }
    """
    # คำนวณสัดส่วนรวมในแต่ละ SECTION
    grp = df.groupby(['SECTION_NAME', 'Activity'])['Values'].sum()
    # ratio per section
    section_target_df = (
        grp.groupby(level=0, group_keys=False)
           .apply(lambda x: x / x.sum())
           .reset_index(name='TargetRatio')
    )
    # เปลี่ยนเป็น dict
    section_target: Dict[str, Dict[str, float]] = defaultdict(dict)
    for _, row in section_target_df.iterrows():
        sec = row['SECTION_NAME']
        act = row['Activity']
        section_target[sec][act] = row['TargetRatio']

    # จำนวนพนักงานในแต่ละ SECTION
    employee_counts = df.groupby('SECTION_NAME')['EMPLOYEE_ID'].nunique().to_dict()

    # สร้าง initial quota โดย round(target_ratio * count)
    section_quota: Dict[str, Dict[str, int]] = {}
    for sec, targets in section_target.items():
        count = employee_counts[sec]
        section_quota[sec] = {
            act: round(ratio * count)
            for act, ratio in targets.items()
        }
        # ปรับ quota ให้ sum == count
        _adjust_quota_for_section(section_quota[sec], targets, count)
        logging.info(f"Section '{sec}': quota adjusted to sum {sum(section_quota[sec].values())} for {count} employees")

    return section_quota, section_target


def _adjust_quota_for_section(
    quota: Dict[str, int],
    target: Dict[str, float],
    total_emp: int
) -> None:
    """
    ปรับ quota dict (in-place) ให้ sum(quota.values()) == total_emp
    โดยแจกเพิ่มให้ activity ที่มี target ratio สูงสุด หรือ ลดจากต่ำสุด
    """
    current = sum(quota.values())
    diff = total_emp - current
    if diff == 0:
        return

    # แปลงให้เป็น list of (activity, target_ratio)
    items = sorted(target.items(), key=lambda x: x[1], reverse=True)
    if diff > 0:
        # ต้องแจกเพิ่ม
        idx = 0
        for _ in range(diff):
            act = items[idx % len(items)][0]
            quota[act] += 1
            idx += 1
    else:
        # ลด quota (diff negative)
        idx = len(items) - 1
        for _ in range(-diff):
            act = items[idx % len(items)][0]
            if quota[act] > 0:
                quota[act] -= 1
            idx -= 1


def assign_forced(df: pd.DataFrame) -> Tuple[List[Dict], set]:
    """
    หาพนักงานที่เลือกกิจกรรมเดียว 100% (Values == 1.0)
    คืนค่า:
      forced_assignments: list of dicts for these employees
      forced_ids: set of EMPLOYEE_ID
    """
    forced = df.groupby('EMPLOYEE_ID').filter(lambda g: len(g) == 1 and g['Values'].iloc[0] == 1.0)
    forced_ids = set()
    assignments = []
    for _, row in forced.iterrows():
        emp_id = row['EMPLOYEE_ID']
        forced_ids.add(emp_id)
        assignments.append({
            'EMPLOYEE_ID': emp_id,
            'NAME': row['NAME'],
            'SECTION_NAME': row['SECTION_NAME'],
            'AssignedActivity': row['Activity']
        })
    logging.info(f"Forced assignments: {len(forced_ids)} employees")
    return assignments, forced_ids


def assign_greedy(
    df: pd.DataFrame,
    section_quota: Dict[str, Dict[str, int]],
    forced_ids: set
) -> List[Dict]:
    """
    จัดสรรแบบ Greedy + Section-aware quota
    รับ:
      df_sorted  — DataFrame เรียงตาม ['EMPLOYEE_ID','Values'] descending
      section_quota
      forced_ids
    คืน:
      assignments: list of dict
    """
    # เรียง data
    df_sorted = df.sort_values(by=['EMPLOYEE_ID', 'Values'], ascending=[True, False])
    # init used quota
    used = {sec: {act: 0 for act in acts} for sec, acts in section_quota.items()}
    assignments = []

    all_emp = set(df['EMPLOYEE_ID'].unique())

    # นับ forced ไปก่อน
    for a in assignments:
        used[a['SECTION_NAME']][a['AssignedActivity']] += 1

    # จัดสรรคนที่ไม่ forced
    for emp_id, grp in df_sorted.groupby('EMPLOYEE_ID'):
        if emp_id in forced_ids:
            continue
        sec = grp['SECTION_NAME'].iloc[0]
        for _, row in grp.iterrows():
            act = row['Activity']
            if used[sec].get(act, 0) < section_quota[sec].get(act, 0):
                assignments.append({
                    'EMPLOYEE_ID': emp_id,
                    'NAME': row['NAME'],
                    'SECTION_NAME': sec,
                    'AssignedActivity': act
                })
                used[sec][act] += 1
                break

    # fallback สำหรับคนที่ยังไม่ได้ assign
    assigned_ids = {a['EMPLOYEE_ID'] for a in assignments} | forced_ids
    unassigned = all_emp - assigned_ids
    for emp_id in unassigned:
        grp = df[df['EMPLOYEE_ID'] == emp_id].sort_values('Values', ascending=False).iloc[0]
        assignments.append({
            'EMPLOYEE_ID': emp_id,
            'NAME': grp['NAME'],
            'SECTION_NAME': grp['SECTION_NAME'],
            'AssignedActivity': grp['Activity']
        })
    logging.info(f"Total assigned (including forced & greedy & fallback): {len(assignments)}")
    return assignments


def save_results(assignments: List[Dict], output_csv: str) -> None:
    """
    บันทึก assignments list ลง CSV
    """
    df_out = pd.DataFrame(assignments)
    df_out.to_csv(output_csv, index=False)
    logging.info(f"Saved results to {output_csv}")


def main():
    parser = argparse.ArgumentParser(
        description="Greedy Section-aware Assignment Script"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="path to input CSV file")
    parser.add_argument("--output", "-o", required=True,
                        help="path to output CSV file")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    df = load_data(args.input)
    section_quota, _ = compute_section_quota(df)
    forced_assignments, forced_ids = assign_forced(df)
    greedy_assignments = assign_greedy(df, section_quota, forced_ids)

    # รวม forced + greedy
    all_assignments = forced_assignments + greedy_assignments
    save_results(all_assignments, args.output)


if __name__ == "__main__":
    main()
