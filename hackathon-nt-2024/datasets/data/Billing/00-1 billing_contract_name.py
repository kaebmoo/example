
import glob
import os
from pathlib import Path
import pandas as pd
from itertools import zip_longest  # For handling lists of unequal length
from tqdm import tqdm


# Specify your dataset directory (adjust to your actual path)
base_path = "datasets/data/Billing/"
files = ["BP_6601.txt", "BP_6604.txt", "BP_6605.txt"]

# ['ACCOUNT_NO', 'TEL_NO', 'PRODUCT DESC', 'ACCOUNT_TYPE', 'CONTRACRT NAME TH', 'CONTRACT TYPE', 'AMOUNT_DUE']
columns = ['ACCOUNT_NO', 'TEL_NO', 'PRODUCT DESC', 'ACCOUNT_TYPE', 'CONTRACRT NAME TH', 'CONTRACT TYPE']


df_output = pd.DataFrame()
for file in tqdm(files):
    df = pd.read_csv(os.path.join(base_path, file), usecols=columns, sep="|", encoding="ISO-8859-11", on_bad_lines="skip", dtype=str)

    # Drop duplicates based on specified columns
    df = df.drop_duplicates(subset=columns)

    df_output = pd.concat([df_output, df])

df_output = df_output.drop_duplicates(subset=columns)
# df_output.loc[:,"AMOUNT_DUE"] = pd.to_numeric(df_output["AMOUNT_DUE"], errors='coerce')
# df_output = df_output.groupby(['ACCOUNT_NO', 'TEL_NO', 'PRODUCT DESC', 'ACCOUNT_TYPE', 'CONTRACRT NAME TH', 'CONTRACT TYPE'])['AMOUNT_DUE'].mean()
df_output.to_csv("datasets/data/Billing/CONTRACT_PACKAGE_NAME.csv", index=False)