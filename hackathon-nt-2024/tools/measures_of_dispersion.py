import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# โหลดข้อมูล Iris dataset
iris = sns.load_dataset('iris')

# ตรวจสอบข้อมูลเบื้องต้น
print(iris.head())
print(iris.describe())

# หา Range
# คำนวณ Range ของความยาวกลีบดอกไม้ (petal length)
petal_length_range = iris['petal_length'].max() - iris['petal_length'].min()
print(f"Range of Petal Length: {petal_length_range}")

#
# คำนวณ Variance และ Standard Deviation ของความยาวกลีบดอกไม้ (petal length)
petal_length_variance = iris['petal_length'].var()
petal_length_std = iris['petal_length'].std()
print(f"Variance of Petal Length: {petal_length_variance}")
print(f"Standard Deviation of Petal Length: {petal_length_std}")

# คำนวณ IQR ของความยาวกลีบดอกไม้ (petal length)
Q1 = iris['petal_length'].quantile(0.25)
Q3 = iris['petal_length'].quantile(0.75)
IQR = Q3 - Q1
print(f"Interquartile Range of Petal Length: {IQR}")

# สร้าง boxplot ของความยาวกลีบดอกไม้ (petal length)
plt.figure(figsize=(10, 6))
sns.boxplot(x='species', y='petal_length', data=iris)
plt.title('Boxplot of Petal Length by Species')
plt.xlabel('Species')
plt.ylabel('Petal Length (cm)')
plt.show()

# สร้างกราฟแสดงการกระจายตัวของความยาวกลีบดอกไม้ (petal length)
plt.figure(figsize=(10, 6))
sns.histplot(iris['petal_length'], kde=True)
plt.title('Distribution of Petal Length')
plt.xlabel('Petal Length (cm)')
plt.ylabel('Frequency')
plt.show()
