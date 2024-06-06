import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import seaborn as sns

# Define a function to label DAYS_DIFF
def label_days_diff(days):
    if days >= 28 and days <= 38:
        return (days - 28) // 3 + 1  # Mapping days to values 1 to 4 within the range
    else:
        return 0


# Read data from CSV file
data_path = "datasets/data/Payments/Payment Product.csv"  # Replace with your actual CSV file path
df = pd.read_csv(data_path)

# Explore and Clean Data
print(df.head())  # Print the first few rows
print(df.info())  # Print data types and summary
print(df.isnull().sum())  # Check for missing values

# สุ่มตัวอย่างข้อมูล (เช่น สุ่มตัวอย่าง 10% ของข้อมูล)
df = df.sample(frac=0.8, random_state=1)
target = (df['DAYS_DIFF'] >= 0) & (df['DAYS_DIFF'] <= 90)
df = df[target]

# Apply the function to create a new column
df['DELAY'] = df['DAYS_DIFF'].apply(label_days_diff)

# Handle missing values (example: remove rows with missing payment_type)
# df.dropna(subset=['payment_type'], inplace=True)

# Convert PAYMENT_DATE and INVOICE_DATE to datetime format
df['PAYMENT_DATE'] = pd.to_datetime(df['PAYMENT_DATE'], format='%Y-%m-%d')
df['INVOICE_DATE'] = pd.to_datetime(df['INVOICE_DATE'], format='%Y-%m-%d')

# Exploratory Data Analysis (EDA)

# Univariate Analysis (example: distribution of AMOUNT)
# คำนวณยอดรวมของ AMOUNT สำหรับแต่ละ DAYS_DIFF
amount_sum_per_days_diff = df.groupby('DAYS_DIFF')['AMOUNT'].sum().reset_index()
plt.figure(figsize=(12, 6))
sns.barplot(x='DAYS_DIFF', y='AMOUNT', data=amount_sum_per_days_diff)
plt.title('Total Amount per DAYS_DIFF')
plt.xlabel('DAYS_DIFF')
plt.ylabel('Total AMOUNT')
plt.xticks(rotation=90)  # หมุน label ของแกน x หากมีค่ามาก
plt.show()

# Bivariate Analysis (example: scatter plot of AMOUNT vs DAYS_DIFF)
plt.scatter(df['DAYS_DIFF'], df['AMOUNT'])
plt.xlabel('Days Between Invoice and Payment')
plt.ylabel('Invoice Amount')
plt.title('Invoice Amount vs. Days Between Invoice and Payment')
plt.show()

# Feature Engineering (Optional)

# แปลงคอลัมน์ PAY_TYPE และ payment_type เป็นตัวเลขโดยใช้ Label Encoding
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['PAY_TYPE'] = le.fit_transform(df['PAY_TYPE'])
df['payment_type'] = le.fit_transform(df['payment_type'])
df['PRODUCT DESC'] = le.fit_transform(df['PRODUCT DESC'])


# Split the data into features (X) and target variable (y)
X = df[['AMOUNT', 'PAY_TYPE', 'payment_type', 'PRODUCT DESC']]  # Features
y = df['DELAY']  # Target variable (DELAY is not provided in the data, you need to calculate it)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model

# Optionally, you can print coefficients and intercept
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# วัดประสิทธิภาพของโมเดล
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R^2 Score: {r2}")

print(y_pred)
