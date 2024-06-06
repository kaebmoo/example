import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
import pandas as pd

# โหลดข้อมูล Iris dataset และสร้าง DataFrame
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target

# แปลงค่า target เป็นชื่อชนิดของดอกไม้
df['species'] = df['species'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})

# แสดงการกระจายตัวของความยาวกลีบดอกไม้ (petal length) สำหรับแต่ละชนิด
sns.displot(df, x='petal length (cm)', hue='species', kind='kde', fill=True)
plt.title('Distribution of Petal Length by Species')
plt.xlabel('Petal Length (cm)')
plt.ylabel('Density')
plt.show()

print(df)
# แสดง boxplot ของความยาวกลีบดอกไม้ (petal length) สำหรับแต่ละชนิด
plt.figure(figsize=(10, 6))
sns.boxplot(x='species', y='petal length (cm)', data=df)
plt.title('Boxplot of Petal Length by Species')
plt.xlabel('Species')
plt.ylabel('Petal Length (cm)')
plt.show()
