import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://root:root1234@localhost:3306/demographics')
df_population = pd.read_sql('SELECT * FROM population_stats', con=engine)
df_fertility = pd.read_sql('SELECT * FROM fertility_stats', con=engine)
df_merged = pd.merge(df_population, df_fertility, on=['alpha_2', 'year'])

columns = ["median_age", "tfr", "births", "pct_0_14", "pct_15_19", "pct_20_39", "pct_40_64", "pct_65_plus"]
df_corr = df_merged[columns].corr()
df_corr.to_excel("correlation_matrix.xlsx")
