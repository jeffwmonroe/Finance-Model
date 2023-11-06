import pandas as pd
import calendar
from datetime import datetime

# import pylab as p

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


def check_debit_credit(debit: float, credit: float, account_no: int) -> str:
    """
    Perform basic error checking on an entry in the trial balances
    """
    if debit == 0 and credit == 0:
        raise Exception(f'({account_no}) credit and debit are both 0')
    if debit < 0:
        raise Exception(f"ERROR: {account_no} debit is a negative number")
    if credit < 0:
        raise Exception(f"ERROR: {account_no} credit is a negative number")
    if debit != 0 and credit != 0:
        raise Exception(f'({account_no}) credit and debit are both NOT 0')
    if credit != 0:
        return 'credit'
    else:
        return 'debit'


def clean_trial_balance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic data cleaning on the monthly trial balance Dataframe
    """
    if len(df.columns) != 4:
        raise Exception(f'error in clean_trial_balance: wrong number of columns: {len(df.columns)}')
    df = df.set_axis(["id", "description", "debit", "credit"], axis=1)
    df = df.astype({'id': int})
    df = df.set_index('id')
    # Some of the monthly trial balances have a total line. We need to remove these lines from the
    # Dataframe. The extra rows do not have an entry in the index
    if 0 in df.index:
        df = df.drop([0])
    return df


def collapse_trail_balance(tb: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    """
    Collapse the credit and debit columns of the trial balance to one column.

    Debit is positive and credit is negative.
    Returns the single column with the date as the header
    """
    day = calendar.monthrange(year, month)[1]
    date = datetime(year, month, day)
    date_str = date.strftime('%Y-%m-%d')
    tb[date_str] = tb['credit'] - tb['debit']
    collapsed_tb = tb[[date_str]]
    total = collapsed_tb[date_str].sum()
    total = round(total, 6)
    if total != 0:
        raise Exception(f'ERROR: trail balances do not sum to zero: {total}')
    return collapsed_tb


def read_trial_balance(xls: pd.ExcelFile, year: int, month_number: int) -> pd.DataFrame:
    """
    Read in the trial balances for a single month.

    This function assumes that the monthly trial balances are in separate tabs and are in order
    The method will check to make certain that the month and year are mentioned in the tab name
    or will raise an exception.

    returns a trial balance Dataframe
    """
    months = [month[0:3].lower() for month in calendar.month_name][1:]
    print(f'year: month = {year} - {months[month_number]} [{month_number}]')
    sheets = xls.sheet_names
    month = months[month_number]
    sheet = sheets[month_number]
    if month not in sheet.lower() or str(year) not in sheet.lower():
        raise Exception(f'Error: tab not found: {year} {month}: {sheet}')
    df = pd.read_excel(xls, sheet_name=month_number, na_values=0)
    df = df.replace(float('nan'), 0)
    df = clean_trial_balance(df)
    return df
