import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Define a function to label DAYS_DIFF
def label_days_diff(days):
    if days >= 28 and days <= 38:
        return (days - 28) // 3 + 1  # Mapping days to values 1 to 4 within the range
    else:
        return 0

# Load ข้อมูลลูกค้าเป็น DataFrame
customer_data = pd.read_csv("datasets/data/Payments/Payment Product.csv" )

# กำหนดตัวแปรเป้าหมาย (1 = ลูกค้าที่มีคุณค่า, 0 = ไม่ใช่ลูกค้าที่มีคุณค่า)
customer_data['is_high_value'] = (customer_data['DAYS_DIFF'] < 38).astype(int)

# Apply the function to create a new column
customer_data['DELAY'] = customer_data['DAYS_DIFF'].apply(label_days_diff)
# Convert PAYMENT_DATE and INVOICE_DATE to datetime format
customer_data['PAYMENT_DATE'] = pd.to_datetime(customer_data['PAYMENT_DATE'], format='%Y-%m-%d')
customer_data['INVOICE_DATE'] = pd.to_datetime(customer_data['INVOICE_DATE'], format='%Y-%m-%d')

le = LabelEncoder()
customer_data['PAY_TYPE'] = le.fit_transform(customer_data['PAY_TYPE'])
customer_data['payment_type'] = le.fit_transform(customer_data['payment_type'])
customer_data['PRODUCT DESC'] = le.fit_transform(customer_data['PRODUCT DESC'])

# Split the data into features (X) and target variable (y)
X = customer_data[['AMOUNT', 'PAY_TYPE', 'payment_type', 'PRODUCT DESC']]  # Features
y = customer_data['is_high_value']  # Target variable (DELAY is not provided in the data, you need to calculate it)

# แบ่งข้อมูลเป็นชุดการฝึกและชุดทดสอบ
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Logistic Regression Model
model = LogisticRegression()
model.fit(X_train, y_train)

# ประเมินประสิทธิภาพของ Model ที่ Test Data
print('Test set accuracy:', model.score(X_test, y_test))

# Make predictions
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