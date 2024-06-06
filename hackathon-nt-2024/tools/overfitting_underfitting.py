import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
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

# สร้างโมเดล Decision Tree เพื่อทดสอบ underfitting และ overfitting
model_tree_underfit = DecisionTreeClassifier(max_depth=1)  # Underfitting
model_tree_underfit.fit(X_train_scaled, y_train)
y_pred_train = model_tree_underfit.predict(X_train_scaled)
y_pred_test = model_tree_underfit.predict(X_test_scaled)
print("Decision Tree (Underfitting) - Training Accuracy:", accuracy_score(y_train, y_pred_train))
print("Decision Tree (Underfitting) - Testing Accuracy:", accuracy_score(y_test, y_pred_test))

model_tree_overfit = DecisionTreeClassifier(max_depth=10)  # Overfitting
model_tree_overfit.fit(X_train_scaled, y_train)
y_pred_train = model_tree_overfit.predict(X_train_scaled)
y_pred_test = model_tree_overfit.predict(X_test_scaled)
print("Decision Tree (Overfitting) - Training Accuracy:", accuracy_score(y_train, y_pred_train))
print("Decision Tree (Overfitting) - Testing Accuracy:", accuracy_score(y_test, y_pred_test))

# แก้ปัญหา Underfitting ด้วยการเพิ่มความซับซ้อนของโมเดล
model_rf = RandomForestClassifier(n_estimators=100)
model_rf.fit(X_train_scaled, y_train)
y_pred_train = model_rf.predict(X_train_scaled)
y_pred_test = model_rf.predict(X_test_scaled)
print("Random Forest - Training Accuracy:", accuracy_score(y_train, y_pred_train))
print("Random Forest - Testing Accuracy:", accuracy_score(y_test, y_pred_test))

# แก้ปัญหา Overfitting ด้วยการใช้ Logistic Regression
model_logistic = LogisticRegression(C=1.0)
model_logistic.fit(X_train_scaled, y_train)
y_pred_train = model_logistic.predict(X_train_scaled)
y_pred_test = model_logistic.predict(X_test_scaled)
print("Logistic Regression - Training Accuracy:", accuracy_score(y_train, y_pred_train))
print("Logistic Regression - Testing Accuracy:", accuracy_score(y_test, y_pred_test))
