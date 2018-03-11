#!/usr/bin/env python3
import sys
import pandas as pd
import collections
from datetime import datetime
import copy

class Parser():
    """Parser for web-scrapped Amazon Mexico (amazon.com.mx) Orders

    Usage:
        $ ./Parser.py webscrappeddata.txt
        $ Saved 10 lines to 2018-03-10T20-24.xls
    """

    def __init__(self):
        pass

    def _text_to_df(self, filename, separator_line):
        with open(filename, 'r') as f:
            lines = f.readlines()
        # strip lines
        lines = [line.strip() for line in lines]
        # remove empty lines
        lines = [line for line in lines if len(line) > 0]
        
        # "item" = "information of a product"

        # Convert the info of all the items into one string
        all_as_string = '\\'.join(lines)
        
        # Have one string per item
        items = all_as_string.split(separator_line)
        
        # Split string of each element
        items = [item.split('\\') for item in items]
        
        # Remove empty values
        for item in items:
            item[:] = [value for value in item if len(value)>0]
        
        # Remove empty lists
        items = [item for item in items if len(item) > 0]

        df = pd.DataFrame(items)
        return df

    def _df_formatter(self, df):
        desired_cols = collections.OrderedDict()
        desired_cols[0] = 'date'
        desired_cols[2] = 'price'
        desired_cols[4] = 'recipient'
        desired_cols[5] = 'order'
        desired_cols[9] = 'product'
        cols_numbers = list(desired_cols.keys())
        df = copy.copy(df.iloc[:, cols_numbers])
        df.columns = list(desired_cols.values())

        # Format column date
        months = {'ENERO':'1',
                  'FEBRERO':'2',
                  'MARZO':'3',
                  'ABRIL':'4',
                  'MAYO':'5',
                  'JUNIO':'6',
                  'JULIO':'7',
                  'AGOSTO':'8',
                  'SEPTIEMBRE':'9',
                  'OCTUBRE':'10',
                  'NOVIEMBRE':'11',
                  'DICIEMBRE':'12'}
        col = df['date'].str.upper()
        for key, val in months.items():
            col = col.str.replace(key, val)
        col = col.str.split(' DE ')
        col = col.apply(lambda x:datetime(int(x[2]), int(x[1]),
                                          int(x[0])))
        df.loc[:, 'date'] = col

        # Format column price
        col = df['price']
        currency_symbol = '$'
        col = col.str.replace(currency_symbol, '')
        thousands_separator = ','
        col = col.str.replace(thousands_separator, '')
        pd.to_numeric(col)
        df.loc[:, 'price'] = col
        return df
        
    def text_to_xls(self, filename, separator_line):
        df = self._text_to_df(filename, separator_line)
        df = self._df_formatter(df)
        output_filename = datetime.today().isoformat().replace(':', '-')[0:16]
        output_filename += '.xls'
        writer = pd.ExcelWriter(output_filename)
        df.to_excel(writer, 'Amazon')
        writer.save()
        print(f"Saved {len(df)} lines to {output_filename}")


if __name__ == '__main__':
    filename = sys.argv[1]
    separator_line = "Pedido realizado"
    instance = Parser()
    instance.text_to_xls(filename, separator_line)
