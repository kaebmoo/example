import pandas as pd

mcr_df = pd.read_csv("/Users/seal/Documents/EE200_Form_Responses.csv")
print(mcr_df.shape)
print(mcr_df.head())

df2 = pd.crosstab(mcr_df.AGE, mcr_df.HOW_OFTEN_TO_EAT)
print(df2)

print(mcr_df.HOW_OFTEN_TO_EAT.str.split(" "))
new_label = mcr_df.HOW_OFTEN_TO_EAT.str.split(" ")
print(new_label.str[1] + " " + new_label.str[0])
mcr_df["HOW_OFTEN_TO_EAT_LABEL"] = new_label.str[1] + " " + new_label.str[0]

print(mcr_df["HOW_OFTEN_TO_EAT_LABEL"])

df2.plot()