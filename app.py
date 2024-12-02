import pandas as pd
import datetime as dt
import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

class db:
    def __init__(self):
        self.transactions = db.transaction_init()
        self.cc = pd.read_csv(r'db/country_codes.csv',index_col=0)
        self.customers = pd.read_csv(r'db/customers.csv',index_col=0)
        self.prod_info = pd.read_csv(r'db/prod_cat_info.csv')

    @staticmethod
    def transaction_init():
        transactions = pd.DataFrame()
        src = r'db/transactions'
        for filename in os.listdir(src):
            transactions = transactions.append(pd.read_csv(os.path.join(src, filename), index_col=0))

        def convert_dates(x):
            try:
                return dt.datetime.strptime(x,'%d-%m-%Y')
            except:
                return dt.datetime.strptime(x,'%d/%m/%Y')
        
        transactions['trans_date'] = transactions['trans_date'].apply(lambda x: convert_dates(x)) # also: .apply(convert_dates)

        return transactions

    def merge(self):
        df = self.transactions.join(
            self.prod_info.drop_duplicates(subset=['prod_cat_code']).set_index('prod_cat_code')['prod_cat'],
            on='prod_cat_code',
            how='left'
        )
        df = df.join(
            self.prod_info.drop_duplicates(subset=['prod_sub_cat_code']).set_index('prod_sub_cat_code')['prod_subcat'],
            on='prod_sub_cat_code',
            how='left'
        )
        df = df.join(
            self.customers.join(
                self.cc,
                on='country_code'
            )
        )
        self.merged = df

db = db()
db.merge()
