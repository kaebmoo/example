import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/webhook/4X6X4BQWKJ9YTBRZXYT1VCTZ9Q', methods=['POST'])
def webhook():
    data = request.get_json()
    query = data['message']['text']  # ดึงข้อความจาก Telegram

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

    return jsonify({'text': response_text})

if __name__ == '__main__':
    app.run(debug=True, port=8080) 
