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

# Inspect
summaries.describe()
summaries.info()
summaries.id.head()
indicators.info()

# Join
df = summaries.join(indicators,
                    how='left',
                    lsuffix='id',
                    rsuffix='id')

df = df.drop(['ID', 'Country'], axis=1)
df.info()

colIds = list(df.columns[list(range(0, 18))])
colVals = list(df.columns[list(range(18, 28))])


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
    (df['value'] == 'Mod'),
    (df['value'] == 'Low'),
    (df['value'] == None)
]

values = [1, 1, 2, 2, 3, None]

df['valueInt'] = np.select(conditions, values, default=df['value'])
df['valueInt'] = df['valueInt'].fillna(0)
df['valueInt'] = pd.to_numeric(df['valueInt'])

df.info()

subCondition = ((df['indicator'] == 'Inflation (%)') | (df['indicator'] == 'Inflation (%)') | (df['indicator'] == 'Food Inflation (%)') | (df['indicator'] == 'Currency Exchange (YoY, %)'))

conditions = [
    (df['valueInt'] > 30) & (df['valueInt'] < 100) & subCondition,
    (df['valueInt'] >= 10) & (df['valueInt'] <= 30) & subCondition,
    (df['valueInt'] > 0) & (df['valueInt'] < 10) & subCondition,
    (df['valueInt'] > -100) & (df['valueInt'] < 0) & subCondition,
    (df['value'] == "")
]

values = [1, 2, 3, 3, None]

df['valueInt'] = np.select(conditions, values, default=df['valueInt'])

df.info()
df.head()



df.to_json(path_or_buf="dataFull.json", orient='values')

indicators.to_json(path_or_buf="dataIndicators.json", orient='values')

df.to_csv("output_filename.csv", index=False, encoding='utf8')
# jsonOutput = dfPivoted.to_json(orient='values')
# parsed = json.loads(jsonOutput)
# json.dumps(parsed, indent=4)
