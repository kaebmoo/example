import pandas as pd

def generate_sql_create_table(df, table_name):
    # Map pandas dtypes to PostgreSQL types
    dtype_mapping = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'datetime64[ns]': 'TIMESTAMP',
        'bool': 'BOOLEAN'
    }

    # Start creating the SQL command
    sql_command = f"CREATE TABLE {table_name} (\n"

    # Loop through each column and map the types
    for column in df.columns:
        dtype = str(df[column].dtype)
        
        if dtype == 'object':
            # Find the maximum length of the data in the column for VARCHAR
            max_length = df[column].str.len().max()
            pg_type = f'VARCHAR({int(max_length)})'
        else:
            # Use the predefined mapping for non-object types
            pg_type = dtype_mapping.get(dtype, 'VARCHAR(255)')  # Default to VARCHAR if not found
        
        sql_command += f"    {column} {pg_type},\n"
    
    # Remove the last comma and add closing bracket
    sql_command = sql_command.rstrip(',\n') + "\n);"

    return sql_command

df = pd.read_csv(r"/Users/seal/Library/CloudStorage/OneDrive-Personal/share/Datasource/2024/co/output/PL_METABASE_2024.csv", dtype=str)
df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')
df['AMOUNT'] = pd.to_numeric(df['AMOUNT'])
df['REVENUE_VALUE'] = pd.to_numeric(df['REVENUE_VALUE'])
df['EXPENSE_VALUE'] = pd.to_numeric(df['EXPENSE_VALUE'])
df['SUB_PRODUCT_KEY'] = pd.to_numeric(df['SUB_PRODUCT_KEY'])
# เติมค่า NaN ด้วย 0
df['SUB_PRODUCT_KEY'] = df['SUB_PRODUCT_KEY'].fillna(0)
df['SUB_PRODUCT_KEY'] = df['SUB_PRODUCT_KEY'].astype(int)

# สร้างคำสั่ง SQL
table_name = "profit_and_loss"
sql = generate_sql_create_table(df, table_name)

print(sql)