import pandas as pd
import glob

# Specify the path and file pattern (adjust the path as necessary)
file_pattern = 'datasets/data/Billing/BP_66*.txt'

# Read all files into a list of DataFrames with the specified options
file_list = glob.glob(file_pattern)
df_list = [pd.read_csv(file, sep="|", encoding="ISO-8859-11", on_bad_lines="warn", dtype=str) for file in file_list]

# Identify common columns
common_columns = set(df_list[0].columns)
for df in df_list[1:]:
    common_columns.intersection_update(df.columns)

# Convert common columns to list
common_columns = list(common_columns)

# Concatenate DataFrames based on common columns
concatenated_df = pd.concat([df[common_columns] for df in df_list], ignore_index=True)

# Show the concatenated DataFrame
print(concatenated_df)
concatenated_df.to_csv("datasets/data/Billing/BP_2023_V1.csv")

