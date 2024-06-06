import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix

url = 'https://github.com/ai-builders/curriculum/raw/main/data/TelcoCustomers.csv'
file = "TelcoCustomers.csv"

# โหลดข้อมูล
data = pd.read_csv(url)

column_name = 'total night minutes'
# วัด Skewness ของคอลัมน์ 'column_name'
skewness = data[column_name].skew()

# แสดงผล
print(skewness)

# แสดงผล Histogram
sns.distplot(data[column_name])
plt.show()

# แสดงผล Density Plot
sns.kdeplot(data[column_name])
plt.show()

# แสดงผล Box Plot
sns.boxplot(y=column_name, data=data)
plt.show()
