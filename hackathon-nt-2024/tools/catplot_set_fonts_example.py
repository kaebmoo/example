import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
# import matplotlib as mpl

# Add font to font manager
fontManager.addfont('/Users/seal/Documents/GitHub/hackathon-nt-2024/datasets/Sarabun/Sarabun-Regular.ttf')
# Set the font for your plot
plt.rcParams['font.family'] = 'Sarabun'
# Set font size for all plot elements
plt.rcParams['font.size'] = 12
# mpl.rc("font", family="Sarabun", size=24)

df = pd.read_csv("/Users/seal/Library/CloudStorage/OneDrive-Personal/share/Datasource/all/revenue/2024/REVENUE_NT_REPORT_2023.csv")

print(df.head())
print(df.dtypes)

df = df[df['SUB_ITEM'] == 5.3]
# วิเคราะห์ยอดขายตามสินค้า
sns.catplot(y='PRODUCT_NAME', x='REVENUE_VALUE', kind='bar', data=df)
plt.show()
