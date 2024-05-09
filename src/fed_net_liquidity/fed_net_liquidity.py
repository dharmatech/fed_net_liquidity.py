import pandas as pd
import fred_pandas
import treasury_gov_pandas
# import newyorkfed_pandas_rrp
import newyorkfed_pandas.rrp

# ----------------------------------------------------------------------
def update_records():
    treasury_gov_pandas.update_records(url='https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance')    
    # newyorkfed_pandas_rrp.update_records(start_date='1900-01-01')
    newyorkfed_pandas.rrp.update_records(start_date='1900-01-01')
    fred_pandas.update_records(series='WALCL')
    fred_pandas.update_records(series='RESPPLLOPNWW')

def load_dataframe():

    tga = treasury_gov_pandas.load_records(url='https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance', update=False)

    tga_a = tga.query('account_type == "Federal Reserve Account"')

    tga_b = tga.query('account_type == "Treasury General Account (TGA)"')

    tga_c = tga.query('account_type == "Treasury General Account (TGA) Closing Balance"')

    tga_all = pd.concat([
        tga_a[['record_date', 'close_today_bal']].rename(columns={'record_date': 'date', 'close_today_bal': 'TGA'}),
        tga_b[['record_date', 'close_today_bal']].rename(columns={'record_date': 'date', 'close_today_bal': 'TGA'}),
        tga_c[['record_date', 'open_today_bal' ]].rename(columns={'record_date': 'date', 'open_today_bal':  'TGA'})
    ])
    # ----------------------------------------------------------------------
    # rrp = newyorkfed_pandas_rrp.load_records(start_date='1900-01-01')

    rrp = newyorkfed_pandas.rrp.load_records(start_date='1900-01-01')

    rrp = rrp.query('not note.str.contains("small value")').query('not note.str.contains("Small Value")')

    # if operationDate is duplicated, keep the row with the highest totalAmtAccepted
    rrp = rrp.sort_values('totalAmtAccepted', ascending=False).drop_duplicates('operationDate')

    rrp = rrp.sort_values('operationDate')    
    # ----------------------------------------------------------------------
    fed = fred_pandas.load_records(series='WALCL')    
    rem = fred_pandas.load_records(series='RESPPLLOPNWW')
    # ----------------------------------------------------------------------
    fed_tmp = fed[['date', 'value']].rename(columns={'value': 'WALCL'})

    rrp_tmp = rrp[['operationDate', 'totalAmtAccepted']].rename(columns={'operationDate': 'date', 'totalAmtAccepted': 'RRP'})

    rem_tmp = rem[['date', 'value']].rename(columns={'value': 'REM'})

    df = fed_tmp

    df = pd.merge(df, rrp_tmp, on='date', how='outer')
    df = pd.merge(df, tga_all, on='date', how='outer')
    df = pd.merge(df, rem_tmp, on='date', how='outer')

    df = df.sort_values('date')

    df = df.ffill()
    # ----------------------------------------------------------------------
    df['WALCL'] = pd.to_numeric(df['WALCL'])
    df['TGA']   = pd.to_numeric(df['TGA'])
    df['REM']   = pd.to_numeric(df['REM'])    
    
    df['WALCL'] = df['WALCL'] * 1000 * 1000
    df['TGA']   = df['TGA'] * 1000 * 1000
    df['REM']   = df['REM'] * 1000 * 1000
    # ----------------------------------------------------------------------
    df['NL'] = df['WALCL'] - df['RRP'] - df['TGA'] - df['REM']

    df['WALCL_diff'] = df['WALCL'].diff()
    df['RRP_diff']   = df['RRP'].diff()
    df['TGA_diff']   = df['TGA'].diff()
    df['REM_diff']   = df['REM'].diff()
    df['NL_diff']    = df['NL'].diff()

    return df
# ----------------------------------------------------------------------
