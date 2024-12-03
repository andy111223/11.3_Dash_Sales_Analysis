import pandas as pd
import datetime as dt
import os
# import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import tab1
import tab2
import tab3

class db:
    def __init__(self):
        self.transactions = db.transaction_init()
        self.cc = pd.read_csv(r'db/country_codes.csv',index_col=0)
        self.customers = pd.read_csv(r'db/customers.csv',index_col=0)
        self.prod_info = pd.read_csv(r'db/prod_cat_info.csv')

    @staticmethod
    def transaction_init():
        src = r'db/transactions'
        transactions_list = []

        for filename in os.listdir(src):
            df = pd.read_csv(os.path.join(src, filename), index_col=0)
            transactions_list.append(df)

        transactions = pd.concat(transactions_list, ignore_index=True)

        def convert_dates(x):
            try:
                return dt.datetime.strptime(x,'%d-%m-%Y')
            except ValueError:
                return dt.datetime.strptime(x,'%d/%m/%Y')
        
        transactions['tran_date'] = transactions['tran_date'].apply(lambda x: convert_dates(x)) # also: .apply(convert_dates)

        return transactions

    def merge(self):
        df = self.transactions.join(
            self.prod_info.drop_duplicates(subset=['prod_cat_code']).set_index('prod_cat_code')['prod_cat'],
            on='prod_cat_code',
            how='left'
        )
        df = df.join(
            self.prod_info.drop_duplicates(subset=['prod_sub_cat_code']).set_index('prod_sub_cat_code')['prod_subcat'],
            on='prod_subcat_code',
            how='left'
        )
        df = df.join(
            self.customers.join(
                self.cc,
                on='country_code'
            )
        )
        self.merged = df

df = db()
df.merge()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Create the app
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Create layout
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Tabs(
                    id='tabs',
                    value='tab-1',
                    children=[
                        dcc.Tab(label='Global Sales',value='tab-1'),
                        dcc.Tab(label='Products',value='tab-2'),
                        dcc.Tab(label='Store Types',value='tab-3')
                    ]
                ),
                html.Div(id='tabs-content') # Placeholder where the content of the active tab will be rendered.
            ],
            style={'width':'80%','margin':'auto'}
        )
    ],
    style={'height':'100%'}
)
# Callback rendering an active tab
@app.callback(
    Output(
        'tabs-content',
        'children'
    ),
    [Input(
        'tabs',
        'value'
    )]
)
def render_content(tab):
    if tab == 'tab-1':
        return tab1.render_tab(df.merged)
    elif tab == 'tab-2':
        return tab2.render_tab(df.merged)
    elif tab == 'tab-3':
        return tab3.render_tab(df.merged)
    
## Tab-1 callbacks
@app.callback(
    Output(
        'bar-sales',
        'figure'
    ),
    [
        Input(
            'sales-range',
            'start_date'
        ),
        Input(
            'sales-range',
            'end_date'
        )
    ]
)
def tab1_bar_sales(start_date,end_date):

    truncated = df.merged[(df.merged['tran_date'] >= start_date) & (df.merged['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby(
        [
            pd.Grouper(
                key='tran_date',
                freq='ME'
            ),
            'Store_type'
        ]
    )['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(
            go.Bar(
                x=grouped.index,
                y=grouped[col],
                name=col,
                hoverinfo='text',
                hovertext=[
                    f'{y/1e3:.2f}k' for y in grouped[col].values
                ]
            )
        )
    data = traces
    fig = go.Figure(
        data=data,
        layout=go.Layout(
            title='Revenue',
            barmode='stack',
            legend=dict(x=0, y=-0.5)
        )
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

