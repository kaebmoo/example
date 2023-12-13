import pandas as pd


df = pd.DataFrame({'Name':['Kathy', 'Linda', 'Peter'],
                   'Gender': ['F','F','M'],
                   'Personal_Status':['Divorced','Married','Married']})

print(df)

df2 = pd.crosstab(df.Personal_Status, df.Gender)

df2.loc['Grand Total']= df2.sum(numeric_only=True, axis=0)
df2.loc[:,'Grand Total'] = df2.sum(numeric_only=True, axis=1)

print(df2)