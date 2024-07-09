import os
import json
import csv
import random
import smtplib
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock

app = Flask(__name__)

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

# กำหนดตัวแปรสำหรับจัดการไฟล์และข้อมูลผู้ใช้ที่ลงทะเบียน
registered_users_file = 'registeredUsersFlask.json'
lock = Lock()

# ฟังก์ชันอ่านข้อมูลจากไฟล์ JSON
def load_registered_users():
    if os.path.exists(registered_users_file):
        with open(registered_users_file, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
                else:
                    # ถ้าข้อมูลที่โหลดไม่ใช่ดิกชันนารี ให้แปลงเป็นดิกชันนารี
                    return {str(i): item for i, item in enumerate(data)}
            except json.JSONDecodeError:
                # ถ้าเกิด JSONDecodeError ให้คืนค่าเป็นดิกชันนารีว่าง
                return {}
    else:
        return {}

# ฟังก์ชันเขียนข้อมูลลงไฟล์ JSON อย่างปลอดภัย
def save_registered_users(data):
    with lock:
        with open(registered_users_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

registered_users = load_registered_users()

# ฟังก์ชันสำหรับสร้างรหัสสุ่ม
def generate_random_code(length):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(characters) for _ in range(length))

# ฟังก์ชันสำหรับส่งอีเมล
def send_activation_email(email, activation_code):
    try:
        smtp_host = 'ncmail.example.com'
        smtp_port = 25
        smtp_user = os.getenv('EMAIL_USER')
        smtp_pass = os.getenv('EMAIL_PASS')

        msg = MIMEMultipart()
        msg['From'] = 'noreply@example.com'
        msg['To'] = email
        msg['Subject'] = 'Activation Code for Your Telegram Bot'
        body = f'Your activation code is: {activation_code}'
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.login(smtp_user, smtp_pass)
        text = msg.as_string()
        server.sendmail(msg['From'], msg['To'], text)
        server.quit()
        print('Email sent successfully')
    except Exception as e:
        print(f'Error sending email: {e}')
        raise e

# อ่านข้อมูลจาก CSV
contacts = []
csv_file = os.getenv('YOUR_CSV_FILE')

if csv_file is None:
    raise ValueError('Environment variable YOUR_CSV_FILE is not set or is empty')


with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        contacts.append(row)

# ฟังก์ชันค้นหาข้อมูล
def search_contact(query):
    return [contact for contact in contacts if any(query in contact[field] for field in contact)]

# ฟังก์ชันส่งข้อความไปยัง Telegram Bot
def send_to_telegram(chat_id, text):
    if not is_debug_mode:
        token = os.getenv('YOUR_TELEGRAM_BOT_TOKEN')
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {'chat_id': chat_id, 'text': text}
        try:
            response = requests.post(url, json=payload)
            print('Message sent:', response.json())
            return response.json()
        except Exception as e:
            print(f'Error sending message: {e}')
    else:
        print(f'Debug message to {chat_id}: \n {text}')

# ฟังก์ชันแบ่งข้อความเป็นส่วนย่อย
def split_message(text, max_length):
    parts = []
    current_part = ''
    for line in text.split('\n'):
        if len(current_part) + len(line) > max_length:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + '\n'
            while len(current_part) > max_length:
                parts.append(current_part[:max_length])
                current_part = current_part[max_length:]
        else:
            current_part += line + '\n'
    if current_part.strip():
        parts.append(current_part.strip())
    return parts

# กำหนดตัวแปรสภาพแวดล้อมสำหรับ debug mode
is_debug_mode = os.getenv('DEBUG_MODE') == 'true'

@app.route('/webhook/4X6X4BQWKJ9YTBRZXYT1VCTZ9Q', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message')
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    text = message['text'].strip()

    if text.startswith('/register '):
        email = text.split(' ')[1]
        if not email.endswith('@example.com'):
            send_to_telegram(chat_id, 'กรุณาใส่อีเมลที่ถูกต้องและใช้ domain @example.com เท่านั้น')
            return jsonify(status='success')

        if user_id in registered_users and registered_users[user_id]['activated']:
            send_to_telegram(chat_id, 'คุณได้ลงทะเบียนและยืนยันแล้ว สามารถใช้งาน bot ได้เลย')
            return jsonify(status='success')

        activation_code = generate_random_code(6)
        registered_users[user_id] = {'email': email, 'activation_code': activation_code, 'activated': False}
        save_registered_users(registered_users)

        try:
            send_activation_email(email, activation_code)
            send_to_telegram(chat_id, f'อีเมลยืนยันได้ถูกส่งไปยัง {email} กรุณาเช็ครหัสยืนยันจากอีเมลของคุณ')
        except Exception as e:
            print(f'Error: {e}')
            send_to_telegram(chat_id, 'เกิดข้อผิดพลาดในการส่งอีเมลยืนยัน')

        return jsonify(status='success')

    if text.startswith('/activate '):
        code = text.split(' ')[1]
        user = registered_users.get(user_id)

        if not user:
            send_to_telegram(chat_id, 'คุณยังไม่ได้ลงทะเบียน: \nสามารถลงทะเบียนโดยใช้ email ของคุณด้วยคำสั่ง /register email@address')
            return jsonify(status='success')

        if user['activation_code'] == code:
            user['activated'] = True
            save_registered_users(registered_users)
            send_to_telegram(chat_id, 'การยืนยันสำเร็จ คุณสามารถใช้งาน bot ได้แล้ว')
        else:
            send_to_telegram(chat_id, 'รหัสยืนยันไม่ถูกต้อง')

        return jsonify(status='success')

    user = registered_users.get(user_id)
    if not user or not user['activated']:
        send_to_telegram(chat_id, "คุณต้องลงทะเบียนและยืนยันด้วยรหัสที่ได้รับทาง email ก่อนจึงจะสามารถใช้งาน bot นี้ได้: \nด้วยคำสั่ง /register email@address\nและยืนยันด้วย code ที่ได้รับทาง email ด้วยคำสั่ง /activate code")
        return jsonify(status='success')

    if len(text) < 2:
        send_to_telegram(chat_id, "กรุณาป้อนข้อความค้นหาที่มีความยาวอย่างน้อย 2 ตัวอักษร")
        return jsonify(status='success')

    if text.isdigit() and len(text) < 9:
        send_to_telegram(chat_id, "กรุณาป้อนหมายเลขที่มีความยาวอย่างน้อย 9 ตัวอักษร")
        return jsonify(status='success')

    if "@example.com" in text:
        send_to_telegram(chat_id, "ผลการค้นหามีมากเกินไป. กรุณาป้อนข้อความค้นหาที่เฉพาะเจาะจงมากขึ้น.")
        return jsonify(status='success')

    print('Received query:', text)
    results = search_contact(text)

    MAX_RESULTS = 100
    if len(results) > MAX_RESULTS:
        send_to_telegram(chat_id, f'ผลการค้นหามีมากเกินไป ({len(results)} รายการ). กรุณาป้อนข้อความค้นหาที่เฉพาะเจาะจงมากขึ้น.')
        return jsonify(status='success')

    response_text = ""
    if results:
        for row in results:
            response_text += f"ชื่อ: {row['ชื่อ-นามสกุล']}\n"
            response_text += f"ชื่อ-อังกฤษ: {row['ชื่อ-อังกฤษ']} {row['นามสกุล-อังกฤษ']}\n"
            response_text += f"ตำแหน่ง: {row['ตำแหน่ง']}\n"
            response_text += f"อีเมล: {row['e-mail']}\n"
            response_text += f"ส่วนงาน: {row['ชื่อเต็มส่วนงาน']}\n"
            response_text += f"โทรศัพท์: {row['โทรศัพท์']}\n\n"
        response_text += f"พบข้อมูลที่ตรงกัน {len(results)} รายการ.\n\n"
    else:
        response_text = "ไม่พบข้อมูลที่ตรงกัน"

    messages = split_message(response_text, 4096)
    for message in messages:
        send_to_telegram(chat_id, message)

    return jsonify(status='success')

if __name__ == '__main__':
    app.run(port=8181, debug=True)
