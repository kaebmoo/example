import pandas as pd

# โหลดข้อมูล
data = pd.read_csv('./tools/customer_profile_active.csv')

# แสดงข้อมูลเบื้องต้น
print(data.head())
print(data.info())

# ตรวจสอบค่าที่หายไป
print(data.isnull().sum())

# กำจัดหรือแทนที่ค่าที่หายไป (ในที่นี้เราเลือกที่จะลบแถวที่มีค่าหายไป)
data_cleaned = data.dropna()

print(data_cleaned.info())

# วิเคราะห์ประเภทลูกค้า
customer_type_counts = data_cleaned['customer_type_name'].value_counts()
print(customer_type_counts)

# วิเคราะห์ราคาของโปรโมชั่น
package_price_stats = data_cleaned['package_price'].describe()
print(package_price_stats)

# แปลงข้อมูลวันที่เป็น datetime object
data_cleaned['install_date'] = pd.to_datetime(data_cleaned['install_date'])
data_cleaned['package_startdate'] = pd.to_datetime(data_cleaned['package_startdate'])
data_cleaned['package_enddate'] = pd.to_datetime(data_cleaned['package_enddate'])

# สร้างคุณสมบัติใหม่จากวันที่ เช่น ระยะเวลาในการใช้งานโปรโมชั่น
data_cleaned['promotion_duration_days'] = (data_cleaned['package_enddate'] - data_cleaned['package_startdate']).dt.days
print(data_cleaned['promotion_duration_days'])

# ตัวอย่างการสร้างโมเดลเพื่อคาดการณ์ลูกค้าที่อาจสนใจในสินค้า/บริการใหม่
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# เลือกคุณสมบัติที่เกี่ยวข้อง (ในที่นี้ใช้ตัวอย่างบางคุณสมบัติ)
features = ['promotion_duration_days', 'package_price']
X = data_cleaned[features]
y = data_cleaned['customer_type_name']  # สมมติว่าเราต้องการคาดการณ์ประเภทลูกค้า

# แบ่งข้อมูลเป็นชุดฝึกอบรมและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# สร้างและฝึกโมเดล Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ทำนายผลและวัดประสิทธิภาพ
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
