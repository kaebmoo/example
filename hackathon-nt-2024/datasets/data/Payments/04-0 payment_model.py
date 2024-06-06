import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colormaps  # Import colormaps

pd.options.display.float_format = '{:,.2f}'.format
# ปิดการแสดงคำเตือน SettingWithCopyWarning ชั่วคราว
pd.options.mode.chained_assignment = None  # ปิดการแสดงคำเตือน

from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

# Define a function to label DAYS_DIFF
def label_days_diff(days):
    if days >= 28 and days <= 38:
        return (days - 28) // 3 + 1  # Mapping days to values 1 to 4 within the range
    else:
        return 0
    
# อ่านข้อมูลจากไฟล์ CSV
data_path = "datasets/data/Payments/Payment Product.csv" 
df = pd.read_csv(data_path)  # แทนที่ 'your_file.csv' ด้วยชื่อไฟล์ของคุณ

# แปลงคอลัมน์ 'PAYMENT_DATE' และ 'INVOICE_DATE' เป็น datetime
df['PAYMENT_DATE'] = pd.to_datetime(df['PAYMENT_DATE'])
df['INVOICE_DATE'] = pd.to_datetime(df['INVOICE_DATE'])
# Extract day of month
df['DAY_OF_MONTH'] = df['PAYMENT_DATE'].dt.day

# สุ่มตัวอย่างข้อมูล (เช่น สุ่มตัวอย่าง 10% ของข้อมูล)
df = df.sample(frac=0.2, random_state=1)
target = (df['DAYS_DIFF'] >= 0) & (df['DAYS_DIFF'] <= 180)
df = df[target]
# Apply the function to create a new column
df['DELAY'] = df['DAYS_DIFF'].apply(label_days_diff)

# แปลงคอลัมน์ PAY_TYPE และ payment_type เป็นตัวเลขโดยใช้ Label Encoding
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['PAY_TYPE'] = le.fit_transform(df['PAY_TYPE'])
df['payment_type'] = le.fit_transform(df['payment_type'])
# PRODUCT DESC
df['PRODUCT DESC'] = le.fit_transform(df['PRODUCT DESC'])

# กำหนด features (ตัวแปรอิสระ) และ target (ตัวแปรตาม)
# แบ่งข้อมูลออกเป็น features และ target
features = df[['AMOUNT', 'PAY_TYPE', 'payment_type', 'PRODUCT DESC', 'DAY_OF_MONTH']]
target = df['DELAY']

# แบ่งข้อมูลเป็นชุด Train และ Test
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# สร้างแบบจำลอง Decision Tree Classifier
model = DecisionTreeClassifier()

# ฝึก (Train) แบบจำลอง
model.fit(X_train, y_train)

# ทำนายข้อมูลที่ใช้ Test
y_pred = model.predict(X_test)

# วัดประสิทธิภาพของโมเดล
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")
# print("Confusion Matrix:")
# print(conf_matrix)
# print("Classification Report:")
# print(class_report)