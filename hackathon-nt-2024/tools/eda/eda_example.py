# Exploratory Data Analysis
# การวิเคราะห์ข้อมูลเชิงการตรวจสอบ 

# https://chetnetisrisaan.medium.com/การวิเคราะห์ข้อมูลเชิงการตรวจสอบ-exploratory-data-analysis-เครื่องมือใหม่ของ-นักวิทยาศาสตร์ข้อมูล-cb31fff3843e

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("datasets/example/Telecom Churn Rate Dataset.xlsx")
# หาจำนวนค่าว่าง
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cmap="viridis", cbar=False, yticklabels=False)
plt.title('Heatmap of Null Values in DataFrame')
plt.show()

# หาจำนวนความถี่ การกระจายตัว และ ค่าผิดปกติ (Outliers)
# Histogram ของ Column1
# การวิเคราะห์จำนวนความถี่ (Frequency Analysis) ด้วย Histogram
plt.figure(figsize=(10, 6))
sns.histplot(df['tenure'], kde=True)
plt.title('Histogram of tenure')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.show()

# การวิเคราะห์การกระจายตัว (Distribution Analysis) ด้วย Boxplot และ Violin plot
# Boxplot ของ Column1
# การระบุค่าผิดปกติ (Outliers Detection) ด้วย Boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(x=df['MonthlyCharges'])
plt.title('Boxplot of Monthly Charges')
plt.xlabel('Values')
plt.show()

# Violin plot ของ Column1
plt.figure(figsize=(10, 6))
sns.violinplot(x=df['tenure'])
plt.title('Violin plot of tenure')
plt.xlabel('Values')
plt.show()

# Convert non-numeric columns to NaN
df["tenure"] = pd.to_numeric(df["tenure"], errors='coerce')
df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors='coerce')
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors='coerce')
df["tenure"].fillna(0, inplace=True)
df["MonthlyCharges"].fillna(0, inplace=True)
df["TotalCharges"].fillna(0, inplace=True)
plt. figure(figsize= (6,4))
sns.heatmap(df[["tenure", "MonthlyCharges","TotalCharges"]].corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Matrix Heatmap')
plt.show()