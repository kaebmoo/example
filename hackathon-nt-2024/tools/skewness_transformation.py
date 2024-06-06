import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

# สร้างตัวอย่างข้อมูลที่มีค่า Skewness ไม่สมมาตร
np.random.seed(0)
data = np.random.exponential(scale=2, size=1000)

# คำนวณค่า Skewness ก่อนการแปลงข้อมูล
original_skewness = stats.skew(data)
print(f"Original Skewness: {original_skewness}")

# แปลงข้อมูลโดยใช้ Log Transformation
log_transformed_data = np.log1p(data)  # ใช้ log(1 + data) เพื่อหลีกเลี่ยง log(0)

# แปลงข้อมูลโดยใช้ Square Root Transformation
sqrt_transformed_data = np.sqrt(data)

# แปลงข้อมูลโดยใช้ Box-Cox Transformation
boxcox_transformed_data, fitted_lambda = stats.boxcox(data)

# คำนวณค่า Skewness หลังการแปลงข้อมูล
log_skewness = stats.skew(log_transformed_data)
sqrt_skewness = stats.skew(sqrt_transformed_data)
boxcox_skewness = stats.skew(boxcox_transformed_data)

print(f"Log Transformed Skewness: {log_skewness}")
print(f"Square Root Transformed Skewness: {sqrt_skewness}")
print(f"Box-Cox Transformed Skewness: {boxcox_skewness}")

# วาดกราฟเปรียบเทียบการกระจายตัวก่อนและหลังการแปลงข้อมูล
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

sns.histplot(data, kde=True, ax=axes[0, 0])
axes[0, 0].set_title('Original Data')

sns.histplot(log_transformed_data, kde=True, ax=axes[0, 1])
axes[0, 1].set_title('Log Transformed Data')

sns.histplot(sqrt_transformed_data, kde=True, ax=axes[1, 0])
axes[1, 0].set_title('Square Root Transformed Data')

sns.histplot(boxcox_transformed_data, kde=True, ax=axes[1, 1])
axes[1, 1].set_title('Box-Cox Transformed Data')

plt.tight_layout()
plt.show()
