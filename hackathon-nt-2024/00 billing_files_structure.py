import glob
import pandas as pd
from itertools import zip_longest  # For handling lists of unequal length


# Specify your dataset directory (adjust to your actual path)
base_path = "datasets/data/Billing/"

# Find all CSV files
csv_files = glob.glob(base_path + "BP_66*.txt")

headers_list = []
headers_with_filenames = []

# Read the header of each CSV file
for file_path in csv_files:
    headers = pd.read_csv(file_path, nrows=0, sep="|", encoding="ISO-8859-11", on_bad_lines="warn", dtype=str).columns.tolist()
    print(f"\nHeaders from {file_path}: {headers}")
    headers_list.append(headers)
    # Create a list where the last element is the filename
    row = headers + [file_path.split("/")[-1]] 
    headers_with_filenames.append(row)
    
print(headers_list)

df_headers = pd.DataFrame(list(zip_longest(*headers_list))).fillna('')
print(df_headers)
df_headers.to_excel("header_columns.xlsx", index=False)

# Create the DataFrame
df_headers = pd.DataFrame(headers_with_filenames)

print(df_headers)
df_headers.to_excel("header_columns_files.xlsx", index=False)