การใช้ `displot` และ `boxplot` ด้วย Python สำหรับการวิเคราะห์ข้อมูลสามารถช่วยให้คุณเห็นการกระจายตัวของข้อมูลและการเปรียบเทียบค่าต่างๆ ได้ง่ายขึ้น

### ตัวอย่างการใช้ `displot` และ `boxplot`

เราจะใช้ข้อมูล Iris dataset จากไลบรารี `seaborn` ในตัวอย่างนี้:

```python
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
```

### การใช้ `displot` (Distribution Plot)

`displot` ใช้สำหรับการแสดงการกระจายตัวของข้อมูล เช่น histogram หรือ kernel density estimate (KDE):

```python
# แสดงการกระจายตัวของความยาวกลีบดอกไม้ (petal length) สำหรับแต่ละชนิด
sns.displot(df, x='petal length (cm)', hue='species', kind='kde', fill=True)
plt.title('Distribution of Petal Length by Species')
plt.xlabel('Petal Length (cm)')
plt.ylabel('Density')
plt.show()
```

### การใช้ `boxplot`

`boxplot` ใช้สำหรับการแสดงการกระจายตัวของข้อมูลและการเปรียบเทียบค่าของข้อมูลในกลุ่มต่างๆ:

```python
# แสดง boxplot ของความยาวกลีบดอกไม้ (petal length) สำหรับแต่ละชนิด
plt.figure(figsize=(10, 6))
sns.boxplot(x='species', y='petal length (cm)', data=df)
plt.title('Boxplot of Petal Length by Species')
plt.xlabel('Species')
plt.ylabel('Petal Length (cm)')
plt.show()
```

### คำอธิบาย

1. **การเตรียมข้อมูล**:
   - โหลดข้อมูล Iris dataset และสร้าง DataFrame
   - แปลงค่า target เป็นชื่อชนิดของดอกไม้เพื่อให้เข้าใจง่ายขึ้น

2. **การใช้ `displot`**:
   - ใช้ `sns.displot` เพื่อแสดงการกระจายตัวของความยาวกลีบดอกไม้ (petal length) สำหรับแต่ละชนิดของดอกไม้
   - กำหนด `kind='kde'` เพื่อแสดงกราฟ KDE (Kernel Density Estimate)
   - กำหนด `hue='species'` เพื่อแสดงข้อมูลแยกตามชนิดของดอกไม้

3. **การใช้ `boxplot`**:
   - ใช้ `sns.boxplot` เพื่อแสดง boxplot ของความยาวกลีบดอกไม้ (petal length) สำหรับแต่ละชนิดของดอกไม้
   - กำหนด `x='species'` และ `y='petal length (cm)'` เพื่อแสดงการเปรียบเทียบค่าความยาวกลีบดอกไม้ในแต่ละชนิดของดอกไม้

การใช้ `displot` และ `boxplot` ช่วยให้เห็นภาพรวมของการกระจายตัวของข้อมูลและการเปรียบเทียบค่าต่างๆ ในข้อมูลได้ง่ายและชัดเจนมากขึ้น ซึ่งเป็นประโยชน์ในการวิเคราะห์ข้อมูลเบื้องต้นและการทำความเข้าใจข้อมูลก่อนการสร้างโมเดลทางสถิติหรือการเรียนรู้ของเครื่อง (machine learning).