# Python script to wrangle data to create the json file.

# Load
import pandas as pd
import numpy as np
import json

# For full head viewing options.
pd.options.display.max_columns = None
pd.options.display.max_rows = None

summaries = pd.read_excel('data_entry.xlsx', 'summaries')
indicators = pd.read_excel('data_entry.xlsx', 'indicators')
mvam = pd.read_excel('data_entry.xlsx', 'mvam')

# Inspect
summaries.describe()
summaries.info()
summaries.id.head()

# Join
df = summaries.merge(indicators,
                    how='left',
                    left_on='id',
                    right_on='ID')

df = df.drop(['ID', 'Country'], axis=1)
df[['Overall Vulnerability', 'id']]
indicators[['Overall Vulnerability', 'ID']]

colIds = list(df.columns[list(range(0, 20))])
colVals = list(df.columns[list(range(20, 30))])


# Pivot Longer
df = pd.melt(df,
             id_vars=colIds,
             value_vars=colVals,
             var_name="indicator")

df.info()

# Create a new column and use np.select to assign values to it using our lists as arguments
conditions = [
    (df['value'] == 'Concern'),
    (df['value'] == 'High'),
    (df['value'] == 'Monitor'),
    (df['value'] == 'Moderate'),
    (df['value'] == 'Low'),
    (df['value'] == None)
]

values = [1, 1, 2, 2, 3, None]

df['valueInt'] = np.select(conditions, values, default=df['value'])
df['valueInt'] = df['valueInt'].fillna(0)
df['valueInt'] = pd.to_numeric(df['valueInt'])

# Convert additional indicator valueInt column to discrete categorical variables for color scheme
subCondition = ((df['indicator'] == 'Inflation (%)') | (df['indicator'] == 'Inflation (%)') | (
    df['indicator'] == 'Food Inflation (%)') | (df['indicator'] == 'Currency Exchange (YoY, %)'))

conditions = [
    (df['valueInt'] > 30) & (df['valueInt'] < 100) & subCondition,
    (df['valueInt'] >= 10) & (df['valueInt'] <= 30) & subCondition,
    (df['valueInt'] > 0) & (df['valueInt'] < 10) & subCondition,
    (df['valueInt'] > -100) & (df['valueInt'] < 0) & subCondition,
    (df['value'] == "")
]

values = [1, 2, 3, 3, None]

df['valueInt'] = np.select(conditions, values, default=df['valueInt'])



# Then add a column of icons for the mvam data
conditions = [
    (mvam['status'] == 'Active'),
    (mvam['status'] == 'Upcoming')
]

values = ["<span style='font-size:24px;color:#80bede'><i class='fas fa-wifi'></i>",
          "<span style='font-size:24px;color:#bbbbbb'><i class='fas fa-expand'></i>"]

mvam['icon'] = np.select(conditions, values, default=mvam['status'])


# View
mvam.info()
df.info()
summaries.info()

# Export
df.to_json(path_or_buf="data/main.json", orient='values')
indicators.to_json(path_or_buf="data/indicators.json", orient='values')
mvam.to_json(path_or_buf="data/mvam.json", orient='values')
summaries.to_json(path_or_buf="data/summaries.json", orient='values')

indicators.to_csv("output2.csv", index=False, encoding='utf8')