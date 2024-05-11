import treasury_gov_pandas
import newyorkfed_pandas.rrp
import fred_pandas

def update_records():
    treasury_gov_pandas.load_records(url='https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance', update=True)
    newyorkfed_pandas.rrp.load_records(start_date='1900-01-01', update=True)
    fred_pandas.load_records(series='WALCL', update=True)
    fred_pandas.load_records(series='RESPPLLOPNWW', update=True)

if __name__ == '__main__':
    update_records()