import pandas as pd
from sqlalchemy import create_engine
import re

def extract_alpha2(geo_id):
    match = re.search(r'WO([A-Z]{2})', geo_id)
    if match:
        return match.group(1)
    return None


# Load Data
df = pd.read_csv("/Users/admin/Desktop/Dev10/dev10-midterm/idbzip/idb5yr.txt", sep="|")
df_age = pd.read_csv("/Users/admin/Desktop/Dev10/dev10-midterm/idbzip/idbsingleyear.txt", sep="|")

# Filter Data (Only Columns We Need)
pop_cols = ['POP0_4', 'POP5_9', 'POP10_14',
            'POP15_19', 
            'POP20_24', 'POP25_29', 
            'POP30_34', 'POP35_39', 
            'POP40_44', 'POP45_49', 'POP50_54', 'POP55_59', 'POP60_64', 
            'POP65_69', 'POP70_74', 'POP75_79', 'POP80_84', 'POP85_89', 'POP90_94', 'POP95_99', 'POP100_']
df_pop = df[['#YR', 'GEO_ID'] + pop_cols].copy()

df = df[['#YR', 'GEO_ID', 'POP', 'MEDAGE', 'TFR', 'BIRTHS']]

# GEO_ID to Name
iso_df = pd.read_csv(
    "/Users/admin/Desktop/Dev10/dev10-midterm/all.csv",
    comment="#",  
    usecols=["alpha-2", "name", "region"] 
)

# Aggregate Age Groups
df_pop['0-14'] = df_pop['POP0_4'] + df_pop['POP5_9'] + df_pop['POP10_14']
df_pop['15-19'] = df_pop['POP15_19']
df_pop['20-39'] = df_pop[['POP20_24','POP25_29','POP30_34','POP35_39']].sum(axis=1)
df_pop['40-64'] = df_pop[['POP40_44','POP45_49','POP50_54','POP55_59','POP60_64']].sum(axis=1)
df_pop['65+'] = df_pop[[c for c in pop_cols if c.startswith(('POP65_','POP70_','POP75_','POP80_','POP85_','POP90_','POP95_','POP100_'))]].sum(axis=1)

# Merges DataFrames
df_total = df.merge(
    df_pop[['#YR','GEO_ID','0-14','15-19','20-39','40-64','65+']],
    on=['#YR','GEO_ID'],
    how='left'
)

# Convert age counts to percentages of total population
df_total['pct_0_14'] = df_total['0-14'] / df_total['POP'] * 100
df_total['pct_15_19'] = df_total['15-19'] / df_total['POP'] * 100
df_total['pct_20_39'] = df_total['20-39'] / df_total['POP'] * 100
df_total['pct_40_64'] = df_total['40-64'] / df_total['POP'] * 100
df_total['pct_65_plus'] = df_total['65+'] / df_total['POP'] * 100

# To get country and region names
df_total['alpha_2'] = df_total['GEO_ID'].apply(extract_alpha2)
df_total = df_total.merge(
    iso_df,
    how="left",
    left_on="alpha_2",
    right_on="alpha-2"
)

# Drops unnecessary columns
df_total = df_total.drop(columns=["alpha-2"])
df_total = df_total.drop(columns=['0-14','15-19','20-39','40-64','65+'])

# Drop invalid data
df_total = df_total.dropna()

# Matches with schema names
df_total = df_total.rename(columns={
    'POP': 'population',
    'MEDAGE': 'median_age',
    'BIRTHS': 'births',
    'TFR': 'tfr',
    '#YR': 'year',
})

# Sends to Database
# Engine
engine = create_engine('mysql+mysqlconnector://root:root1234@localhost:3306/demographics')

# Countries
df_countries = df_total[['alpha_2', 'name', 'region']].drop_duplicates()
df_countries.to_sql('countries', con=engine, if_exists='append', index=False)

# Population stats
df_population = df_total[['alpha_2', 'year', 'population', 'median_age', 
                          'pct_0_14', 'pct_15_19', 'pct_20_39', 'pct_40_64', 'pct_65_plus']]
df_population.to_sql('population_stats', con=engine, if_exists='append', index=False)

# Fertility stats
df_fertility = df_total[['alpha_2', 'year', 'births', 'tfr']]
df_fertility.to_sql('fertility_stats', con=engine, if_exists='append', index=False)

print("Data Loaded Successfully")

