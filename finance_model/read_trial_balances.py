import pandas as pd
import calendar
from datetime import datetime

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


def clean_trial_balance(df: pd.DataFrame):
    if len(df.columns) != 4:
        raise Exception(f'error in clean_trial_balance: wrong number of columns: {len(df.columns)}')
    df = df.set_axis(["id", "description", "debit", "credit"], axis=1)
    df = df.astype({'id': int})
    df = df.set_index('id')
    df = df.drop([0])
    return df


def collapse_trail_balance(tb: pd.DataFrame, month, year):
    day = calendar.monthrange(year, month)[1]
    date = datetime(year, month, day)
    date_str = date.strftime('%Y-%m-%d')
    tb[date_str] = tb['debit'] - tb['credit']
    tb = tb[[date_str]]
    total = tb[date_str].sum()
    total = round(total, 6)
    if total != 0:
        raise Exception(f'ERROR: trail balances do not sum to zero: {total}')
    return tb


def read_trial_balance(xls: pd.ExcelFile, year: int, month_number: int):

    months = [month[0:3].lower() for month in calendar.month_name][1:]
    print(f'year: month = {year} - {months[month_number]} [{month_number}]')
    sheets = xls.sheet_names
    month = months[month_number]
    sheet = sheets[month_number]
    if month not in sheet.lower() or str(year) not in sheet.lower():
        print(f'Not Found: {year} {month}: {sheet}')
        return None
    df = pd.read_excel(xls, sheet_name=month_number, na_values=0)
    df = df.replace(float('nan'), 0)
    return df



