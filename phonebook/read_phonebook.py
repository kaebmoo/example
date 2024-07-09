import os
import csv

# อ่านข้อมูลจาก CSV
contacts = []
csv_file = os.getenv('YOUR_CSV_FILE')

with open(csv_file, mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        contacts.append(row)

# ฟังก์ชันค้นหาข้อมูล
def search_contact(query):
    return [contact for contact in contacts if any(query in contact[field] for field in contact)]
