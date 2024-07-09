import pandas as pd
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)

# โหลดค่าตัวแปรจากไฟล์ .env
load_dotenv()

# อ่านค่าตัวแปรจาก .env
TOKEN = os.getenv('YOUR_TELEGRAM_BOT_TOKEN')

file = "/Users/seal/Library/CloudStorage/OneDrive-Personal/share/Datasource/adhoc/NT_Phonebook.csv"
# อ่านข้อมูลจาก CSV หรือแหล่งข้อมูลอื่น ๆ
df = pd.read_csv(file)  # Replace with your actual file path

# ฟังก์ชันค้นหาข้อมูล
def search_contact(query):
    results = df[
        (df['ชื่อ-นามสกุล'].str.contains(query)) | 
        (df['e-mail'].str.contains(query)) |
        (df['โทรศัพท์'].astype(str).str.contains(query))
    ]
    return results

# ฟังก์ชันส่งข้อความไปยัง Telegram Bot
def send_to_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()

@app.route('/webhook/4X6X4BQWKJ9YTBRZXYT1VCTZ9Q', methods=['POST'])
def webhook():
    data = request.get_json()
    query = data['message']['text']  # ดึงข้อความจาก Telegram
    chat_id = data['message']['chat']['id']  # ดึง chat ID จาก Telegram

    results = search_contact(query)

    if not results.empty:
        response_text = "พบข้อมูลที่ตรงกัน:\n\n"
        for _, row in results.iterrows():
            response_text += f"ชื่อ: {row['ชื่อ-นามสกุล']}\n"
            response_text += f"อีเมล: {row['e-mail']}\n"
            response_text += f"ส่วนงาน: {row['ชื่อเต็มส่วนงาน']}\n"
            response_text += f"โทรศัพท์: {row['โทรศัพท์']}\n\n"
            
    else:
        response_text = "ไม่พบข้อมูลที่ตรงกัน"

    app.logger.debug(f'Response text: {response_text}')
    # ส่งข้อความไปยัง Telegram Bot
    send_to_telegram(chat_id, response_text)

    # ส่งการตอบกลับ HTTP 200 ให้กับ Telegram
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
