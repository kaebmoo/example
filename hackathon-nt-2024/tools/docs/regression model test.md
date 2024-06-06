การวัดประสิทธิภาพของโมเดลการถดถอย (regression model) สามารถทำได้โดยใช้ metric ต่างๆ ที่นิยมใช้ เช่น ค่าเฉลี่ยความคลาดเคลื่อน (mean absolute error - MAE), ค่าความคลาดเคลื่อนกำลังสองเฉลี่ย (mean squared error - MSE), รากของค่าความคลาดเคลื่อนกำลังสองเฉลี่ย (root mean squared error - RMSE) และค่าสัมประสิทธิ์การกำหนด (R² score) ใน Python เราสามารถใช้ไลบรารี scikit-learn (sklearn) สำหรับการวัดประสิทธิภาพของโมเดลได้

ตัวอย่างโค้ดสำหรับการวัดประสิทธิภาพของโมเดลการถดถอยด้วย Python:

```python
# นำเข้าไลบรารีที่จำเป็น
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# โหลดข้อมูลตัวอย่าง (เช่น California Housing dataset)
data = fetch_california_housing()
X = data.data
y = data.target

# แบ่งข้อมูลเป็นชุดฝึกอบรมและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# สร้างโมเดล (เช่น Linear Regression)
model = LinearRegression()
model.fit(X_train, y_train)

# ทำนายผลลัพธ์
y_pred = model.predict(X_test)

# วัดประสิทธิภาพของโมเดล
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R^2 Score: {r2}")
```

### คำอธิบาย:

1. **โหลดและแบ่งข้อมูล**: ใช้ `train_test_split` เพื่อแบ่งข้อมูลออกเป็นชุดฝึกอบรมและชุดทดสอบ
2. **สร้างโมเดล**: ในที่นี้เราใช้ Linear Regression และฝึกอบรมโมเดลด้วย `X_train` และ `y_train`
3. **ทำนายผลลัพธ์**: ใช้ `X_test` เพื่อทำนายผลลัพธ์และเก็บผลใน `y_pred`
4. **วัดประสิทธิภาพ**: ใช้ฟังก์ชันต่างๆ จาก `sklearn.metrics` เพื่อคำนวณค่า metric ที่ต้องการ
   - `mean_absolute_error`: คำนวณค่าเฉลี่ยของความคลาดเคลื่อนแบบสัมบูรณ์
   - `mean_squared_error`: คำนวณค่าความคลาดเคลื่อนกำลังสองเฉลี่ย
   - `r2_score`: คำนวณค่าสัมประสิทธิ์การกำหนด (R²) ซึ่งแสดงถึงความแม่นยำของโมเดลในการทำนายค่าที่เป็นจริง

### การประเมินผล:
- **MAE**: ค่าที่ต่ำกว่าหมายถึงโมเดลมีความแม่นยำมากขึ้น
- **MSE และ RMSE**: ค่าที่ต่ำกว่าหมายถึงโมเดลมีความแม่นยำมากขึ้น โดย RMSE นั้นแสดงผลในหน่วยเดียวกับตัวแปรที่ทำนาย
- **R² score**: ค่าที่ใกล้ 1 หมายถึงโมเดลสามารถอธิบายความแปรปรวนของข้อมูลได้ดี

การใช้ metric เหล่านี้ช่วยให้คุณสามารถประเมินประสิทธิภาพของโมเดลการถดถอยและปรับปรุงโมเดลให้ดีขึ้นได้