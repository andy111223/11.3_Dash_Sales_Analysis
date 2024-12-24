from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

def render_tab(df):
    """
    Layout for the 'Store Types' tab. 
    df is the merged DataFrame with transaction, product, and customer data.
    """

    min_date = df['tran_date'].min()
    max_date = df['tran_date'].max()

    # Prepare storetype dropdown
    storetypes = df['Store_type'].dropna().unique()
    storetype_dropdown = dcc.Dropdown(
        id='storetype-dropdown',
        options=[{'label': stype, 'value': stype} for stype in storetypes],
        value=storetypes[0] if len(storetypes) > 0 else None,  
        clearable=False
    )

    layout = html.Div([
        html.H1('Store Type Analysis', style={'text-align': 'center'}),

        html.Div(
            [
                dcc.DatePickerRange(
                    id='storetype-date-range',
                    start_date=min_date,
                    end_date=max_date,
                    display_format='YYYY-MM-DD'
                )
            ],
            style={'width':'100%', 'text-align':'center', 'padding':'10px'}
        ),

        html.Div([
            dcc.Graph(id='weekday-sales')
        ], style={'width': '100%', 'text-align': 'center'}),

        html.Br(),

        html.Div([
            html.Div([
                html.H3('Select Store Type:'),
                storetype_dropdown
            ], style={'width':'25%','display':'inline-block','vertical-align':'top','text-align':'center'}),

            html.Div([
                dcc.Graph(id='storetype-gender-dist'),
                dcc.Graph(id='storetype-country-dist'),
                html.Div(id='storetype-kpi')
            ], style={'width':'70%','display':'inline-block','vertical-align':'top','text-align':'center'})
        ]),
    ])

    return layout
