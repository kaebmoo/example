## การวัดรูปร่าง (Measures of Shape) หรือ Skewness ใน Python

**Skewness**  เป็นการวัดความ**ไม่สมมาตร** ของการกระจายข้อมูล  ค่า Skewness จะบอกเราว่าข้อมูลกระจายไปทางด้านใด  และหางของการกระจายยาวแค่ไหน

**การวัด Skewness ใน Python:**

1. **ใช้ฟังก์ชัน `skew()` จากไลบรารี Pandas:**

```python
import pandas as pd

# โหลดข้อมูล
data = pd.read_csv('data.csv')

# วัด Skewness ของคอลัมน์ 'column_name'
skewness = data['column_name'].skew()

# แสดงผล
print(skewness)
```

2. **ใช้ฟังก์ชัน `kurtosis()` จากไลบรารี SciPy:**

```python
import scipy.stats as stats

# โหลดข้อมูล
data = pd.read_csv('data.csv')

# วัด Skewness ของคอลัมน์ 'column_name'
skewness = stats.skew(data['column_name'])

# แสดงผล
print(skewness)
```

**การตีความค่า Skewness:**

* **ค่า Skewness = 0:**  ข้อมูลกระจาย**สมมาตร**  
* **ค่า Skewness > 0:**  ข้อมูลกระจาย**เบ้ไปทางขวา**  หางยาวทางขวา
* **ค่า Skewness < 0:**  ข้อมูลกระจาย**เบ้ไปทางซ้าย**  หางยาวทางซ้าย

**ตัวอย่าง:**

* **ค่า Skewness = 0.5:**  ข้อมูลกระจายเบ้ไปทางขวาเล็กน้อย  หางยาวทางขวาเล็กน้อย
* **ค่า Skewness = -1.0:**  ข้อมูลกระจายเบ้ไปทางซ้ายมาก  หางยาวทางซ้ายมาก

**หมายเหตุ:**

* ค่า Skewness ที่**มาก**  อาจบ่งบอกถึง**outlier**  ในข้อมูล
* ควรใช้ Skewness ร่วมกับ**วัดรูปร่างอื่นๆ**  เช่น  Kurtosis  เพื่อวิเคราะห์ข้อมูล

**แหล่งข้อมูลเพิ่มเติม:**

* [https://en.wikipedia.org/wiki/Skewness](https://en.wikipedia.org/wiki/Skewness)
* [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.skew.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.skew.html)
* [https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html)

## แสดงผล Skewness แบบกราฟด้วย Python

 Skewness แบบกราฟด้วย Python มีหลายวิธีสำหรับการแสดงผล Skewness แบบกราฟ  ขึ้นอยู่กับความต้องการของคุณ

**วิธีทั่วไป:**

1. **Histogram:**  วาดกราฟแท่ง  แสดงความถี่ของข้อมูลในแต่ละช่วง  Skewness ของข้อมูลจะส่งผลต่อรูปร่างของกราฟ  เช่น  กราฟเบ้ไปทางขวา  แสดงว่าข้อมูลมี Skewness บวก
2. **Density Plot:**  วาดกราฟเส้น  แสดงความหนาแน่นของข้อมูล  Skewness ของข้อมูลจะส่งผลต่อความลาดชันของกราฟ  เช่น  กราฟลาดชันทางขวา  แสดงว่าข้อมูลมี Skewness บวก
3. **Box Plot:**  วาดกล่องแสดงข้อมูล  แสดงค่ากลาง  ค่าควอไทล์ที่ 25% และ 75%  เส้นหนวด  และ outlier  Skewness ของข้อมูลจะส่งผลต่อความยาวของเส้นหนวด  เช่น  เส้นหนวดด้านขวายาวกว่า  แสดงว่าข้อมูลมี Skewness บวก

**ตัวอย่าง:**

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# โหลดข้อมูล
data = pd.read_csv('data.csv')

# แสดงผล Histogram
sns.distplot(data['column_name'])
plt.show()

# แสดงผล Density Plot
sns.kdeplot(data['column_name'])
plt.show()

# แสดงผล Box Plot
sns.boxplot(x='column_name', data=data)
plt.show()
```

**หมายเหตุ:**

* เครื่องมือสร้างกราฟ  มีให้เลือกใช้งานหลายแบบ  เช่น  Matplotlib, Seaborn
* คุณสามารถปรับแต่งกราฟ  เพื่อแสดงผลเพิ่มเติม  เช่น  ใส่ชื่อแกน  ใส่ชื่อกราฟ  ฯลฯ

**แหล่งข้อมูลเพิ่มเติม:**

* [https://seaborn.pydata.org/generated/seaborn.distplot.html](https://seaborn.pydata.org/generated/seaborn.distplot.html)
* [https://seaborn.pydata.org/generated/seaborn.kdeplot.html](https://seaborn.pydata.org/generated/seaborn.kdeplot.html)
* [https://seaborn.pydata.org/generated/seaborn.boxplot.html](https://seaborn.pydata.org/generated/seaborn.boxplot.html)

**นอกจากวิธีเหล่านี้แล้ว  ยังมีวิธีการอื่นๆ  สำหรับการแสดงผล Skewness แบบกราฟ   คุณสามารถค้นหาข้อมูลเพิ่มเติม  บนอินเทอร์เน็ต  หรือปรึกษาผู้เชี่ยวชาญด้าน Data Visualization**
