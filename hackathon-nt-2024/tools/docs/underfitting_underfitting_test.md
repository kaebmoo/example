การตรวจสอบว่ามีการ underfitting หรือ overfitting หรือว่าโมเดลของเราอยู่ในสภาวะที่เหมาะสม (optimum) สามารถทำได้โดยการเปรียบเทียบประสิทธิภาพของโมเดลบนชุดข้อมูลฝึก (training set) และชุดข้อมูลทดสอบ (test set) หากโมเดลมีประสิทธิภาพดีบนชุดข้อมูลฝึกแต่มีประสิทธิภาพต่ำบนชุดข้อมูลทดสอบ แสดงว่าโมเดลมีการ overfitting ในทางตรงกันข้าม หากโมเดลมีประสิทธิภาพต่ำทั้งบนชุดข้อมูลฝึกและชุดข้อมูลทดสอบ แสดงว่าโมเดลมีการ underfitting

### วิธีการตรวจสอบการ underfitting และ overfitting

1. **ใช้กราฟ Learning Curve**:
    - กราฟ Learning Curve แสดงการเปลี่ยนแปลงของความแม่นยำหรือความผิดพลาดของโมเดลเมื่อจำนวนข้อมูลฝึกเพิ่มขึ้น

2. **เปรียบเทียบ Training Score และ Validation Score**:
    - ใช้ค่า score (เช่น accuracy หรือ RMSE) ของข้อมูลฝึกและข้อมูลทดสอบเพื่อเปรียบเทียบ

### ตัวอย่างการตรวจสอบด้วย Python

เราจะใช้ข้อมูล Iris dataset ในตัวอย่างนี้:

```python
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# โหลดข้อมูล Iris dataset
iris = sns.load_dataset('iris')
X = iris.drop('species', axis=1)
y = iris['species']

# แปลงค่าข้อความใน y ให้เป็นค่าตัวเลข
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# แบ่งข้อมูลเป็นชุดฝึกและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.3, random_state=42)

# ปรับขนาดข้อมูล
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# สร้างโมเดล
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# ประเมินผลโมเดล
y_pred_train = model.predict(X_train_scaled)
y_pred_test = model.predict(X_test_scaled)
train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred_test)

print(f"Training Accuracy: {train_accuracy}")
print(f"Testing Accuracy: {test_accuracy}")

# สร้างกราฟ Learning Curve
train_sizes, train_scores, test_scores = learning_curve(model, X_train_scaled, y_train, cv=5, n_jobs=-1, train_sizes=np.linspace(0.1, 1.0, 10))

# คำนวณค่าเฉลี่ยและค่าความเบี่ยงเบนมาตรฐานของคะแนน
train_scores_mean = np.mean(train_scores, axis=1)
train_scores_std = np.std(train_scores, axis=1)
test_scores_mean = np.mean(test_scores, axis=1)
test_scores_std = np.std(test_scores, axis=1)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")

plt.fill_between(train_sizes, train_scores_mean - train_scores_std, train_scores_mean + train_scores_std, alpha=0.1, color="r")
plt.fill_between(train_sizes, test_scores_mean - test_scores_std, test_scores_mean + test_scores_std, alpha=0.1, color="g")

plt.title('Learning Curve')
plt.xlabel('Training examples')
plt.ylabel('Score')
plt.legend(loc="best")
plt.grid()
plt.show()
```

### คำอธิบาย

1. **การเตรียมข้อมูล**:
   - โหลดข้อมูล Iris dataset และแปลงค่าข้อความในคอลัมน์ `species` ให้เป็นค่าตัวเลขโดยใช้ `LabelEncoder`
   - แบ่งข้อมูลเป็นชุดฝึกและชุดทดสอบ และปรับขนาดข้อมูล

2. **การสร้างโมเดลและการประเมินผล**:
   - สร้างโมเดล RandomForestClassifier และฝึกกับข้อมูลฝึก
   - คำนวณค่าความแม่นยำ (accuracy) บนข้อมูลฝึกและข้อมูลทดสอบ

3. **การสร้างกราฟ Learning Curve**:
   - ใช้ `learning_curve` จาก `sklearn.model_selection` เพื่อสร้างกราฟ Learning Curve
   - แสดงกราฟการเปลี่ยนแปลงของคะแนนความแม่นยำ (หรือ score อื่น ๆ) บนข้อมูลฝึกและข้อมูลทดสอบเมื่อจำนวนข้อมูลฝึกเพิ่มขึ้น

### การตีความผลลัพธ์

- **Overfitting**: หากกราฟแสดงให้เห็นว่าความแม่นยำบนข้อมูลฝึกสูงมากแต่ความแม่นยำบนข้อมูลทดสอบต่ำ แสดงว่ามีการ overfitting
- **Underfitting**: หากกราฟแสดงให้เห็นว่าความแม่นยำบนข้อมูลฝึกและข้อมูลทดสอบต่ำ แสดงว่ามีการ underfitting
- **Optimum**: หากกราฟแสดงให้เห็นว่าความแม่นยำบนข้อมูลฝึกและข้อมูลทดสอบมีค่าใกล้เคียงกันและสูง แสดงว่าโมเดลอยู่ในสภาวะที่เหมาะสม

การใช้กราฟ Learning Curve และการเปรียบเทียบประสิทธิภาพของโมเดลบนข้อมูลฝึกและข้อมูลทดสอบช่วยให้เราสามารถระบุได้ว่าโมเดลมีการ underfitting, overfitting หรือว่าอยู่ในสภาวะที่เหมาะสม.