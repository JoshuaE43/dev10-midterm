import os
import plotly.express as px
import pandas as pd
from dash import Dash, dash_table, html, dcc, Input, Output, callback
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://root:root1234@localhost:3306/demographics')
df_countries = pd.read_sql('SELECT * FROM countries', con=engine)
df_population = pd.read_sql('SELECT * FROM population_stats', con=engine)
df_fertility = pd.read_sql('SELECT * FROM fertility_stats', con=engine)

app = Dash()

df_merged = pd.merge(df_population, df_fertility, on=['alpha_2', 'year'])

sctr_plt = px.scatter(
    df_merged,         
    x="median_age",
    y="tfr",
    color="alpha_2",        
    title="Median Age vs TFR"
)

df_merged = pd.merge(df_merged, df_countries, on="alpha_2", how="left")
country_options = []
for i, row in df_countries.iterrows():
    country_options.append({
        "label": row["name"] + " (" + row["region"] + ")",
        "value": row["name"]
    })


df_merged['dominant_age_group'] = df_merged[['pct_0_14','pct_15_19','pct_20_39','pct_40_64','pct_65_plus']].idxmax(axis=1)
# Maps column names to nicer labels
age_labels = {
    'pct_0_14': '0-14',
    'pct_15_19': '15-19',
    'pct_20_39': '20-39',
    'pct_40_64': '40-64',
    'pct_65_plus': '65+'
}
df_merged['dominant_age_group'] = df_merged['dominant_age_group'].map(age_labels)
age_order = ['0-14', '15-19', '20-39', '40-64', '65+']
box_chart = px.box(
    df_merged,
    y="dominant_age_group",   
    x="tfr",
    color="dominant_age_group", 
    points="all", 
    category_orders={"dominant_age_group": age_order},
    title="Fertility Rate by Dominant Age Group",
    labels={"tfr":"Total Fertility Rate", "dominant_age_group":"Dominant Age Group"}
)

years = sorted(df_merged["year"].unique())
start_year = int(years[0])
end_year = int(years[-1])
default_year = start_year
marks_dict = {
    start_year: str(start_year),
    default_year: str(default_year),
    end_year: str(end_year)
}
df_table = df_merged.astype(str)



app.layout = [
    html.H1("Demographic Dashboard"),
    html.Div(
        [
            html.H2("Dataset Overview"),
            html.P("This dashboard uses the following datasets:"),
            html.Ul(
                [
                    html.Li([
                        "International Database: World Population Estimates and Projections – ",
                        html.A(
                            "IDB main page",
                            href="https://www.census.gov/programs-surveys/international-programs/about/idb.html",
                        )
                    ]),
                    html.Li([
                        "IDB 5-Year ",
                        html.A(
                            "Variables/Columns",
                            href="https://api.census.gov/data/timeseries/idb/5year/variables.html",
                        )
                    ]),
                    html.Li([
                        "IDB Single-Year ",
                        html.A(
                            "Variables/Columns",
                            href="https://api.census.gov/data/timeseries/idb/1year/variables.html",
                        )
                    ]),
                    html.Li([
                        "ISO 3166 countries with regional codes - ",
                        html.A(
                            "Code Mappings",
                            href="https://github.com/lukes/ISO-3166-Countries-with-Regional-Codesx",
                        )
                    ])
                ]
            )
        ],
        style={
            "border": "2px solid #4CAF50",
            "padding": "20px",
            "border-radius": "10px",
            "background-color": "#f9f9f9",
            "margin-bottom": "20px",
            "box-shadow": "2px 2px 8px rgba(0,0,0,0.1)"
        }
    ),

    html.H2("APA Citations"),
    html.P("U.S. Census Bureau. (2025). International Database (IDB). https://www.census.gov/programs-surveys/international-programs/about/idb.html"),
    html.P("Arturictus. (n.d.). ISO 3166 countries with regional codes. GitHub. https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes"),

    html.H2("Report"),

    dash_table.DataTable(
        id="report-table",
        data=df_table.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df_merged.columns],
        page_size=25,
        sort_action="native",
        filter_action="native"
    ),

    html.H2("Graphs"),

    dcc.Graph(id="scttr", figure=sctr_plt),
    dcc.Graph(id="box", figure=box_chart),
    dcc.Dropdown(
        id="country-dropdown",
        options=country_options,        
        value=[country_options[0]["value"]],
        multi=True                   
    ),
    dcc.Slider(
        id="year-slider",
        min=start_year,
        max=end_year,
        value=default_year,
        marks=marks_dict,
        step=1
    ),

    html.P("Dev10 Midterm - Joshua Eapen")
    
]


@callback(
    Output("scttr", "figure"),
    Output("box", "figure"),
    Input("country-dropdown", "value"),
    Input("year-slider", "value")

)
def update_chart(selected_countries, selected_year):
    

    filtered_df = df_merged[df_merged["name"].isin(selected_countries)]
    filtered_df = filtered_df[filtered_df["year"] == int(selected_year)]

    scatter_fig = px.scatter(
        filtered_df,         
        x="median_age",
        y="tfr",
        color="alpha_2",        
        title="Median Age vs TFR"
    )


    box_fig = px.box(
        filtered_df,
        y="dominant_age_group",   
        x="tfr",
        color="dominant_age_group", 
        points="all", 
        category_orders={"dominant_age_group": age_order},
        title="Fertility Rate by Dominant Age Group",
        labels={"tfr":"Total Fertility Rate", "dominant_age_group":"Dominant Age Group"}
    )

    return scatter_fig, box_fig

@callback(
    Output("country-dropdown", "options"),
    Output("country-dropdown", "value"),
    Input("year-slider", "value"),
    Input("country-dropdown", "value")
)
def update_countries_for_year(selected_year, selected_countries):
    filtered_df = df_merged[df_merged["year"] == int(selected_year)]
    
    countries_for_year = filtered_df["name"].sort_values().unique()
    options = [{"label": c, "value": c} for c in countries_for_year]
    
    
    if selected_countries:
        value = [c for c in selected_countries if c in countries_for_year]
    else:
        # if nothing was selected before, default to all or first country
        value = countries_for_year.tolist() 

    return options, value



if __name__ == "__main__":
    app.run(debug=True)

