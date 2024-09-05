import pandas as pd
from sqlalchemy import create_engine

df1 = pd.read_csv(r"C:\Users\00320845\OneDrive\share\Datasource\all\revenue\2024\REVENUE_NT_REPORT_2024.csv", dtype=str)
df2 = pd.read_csv(r"C:\Users\00320845\OneDrive\share\Datasource\all\revenue\REVENUE_NT_REPORT_2023.csv")
df3 = pd.read_csv(r"C:\Users\00320845\OneDrive\share\Datasource\all\revenue\REVENUE_NT_REPORT_2022.csv")

df1['DATE'] = pd.to_datetime(df1['DATE'], format='%Y/%m/%d')
df1['AMOUNT'] = pd.to_numeric(df1['AMOUNT'])
df1['REVENUE_VALUE'] = pd.to_numeric(df1['REVENUE_VALUE'])
df1['SUB_PRODUCT_KEY'] = pd.to_numeric(df1['SUB_PRODUCT_KEY'])

# สร้างการเชื่อมต่อกับ PostgreSQL
engine = create_engine('postgresql://seal:chang@localhost:5432/metabase')

# นำข้อมูลเข้าสู่ PostgreSQL
df1.to_sql('revenue', engine, if_exists='replace', index=False)
