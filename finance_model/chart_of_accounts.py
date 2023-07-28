import pandas as pd
from finance_model.ledger import Ledger
from finance_model.timer import timer
from finance_model.read_trial_balances import read_trial_balance, clean_trial_balance, collapse_trail_balance


def check_debit_credit(debit, credit, account_no):
    if debit == 0 and credit == 0:
        raise Exception(f'({account_no}) credit and debit are both 0')
    if debit < 0:
        Exception(f"ERROR: {account_no} debit is a negative number")
    if credit < 0:
        Exception(f"ERROR: {account_no} credit is a negative number")
    if debit != 0 and credit != 0:
        raise Exception(f'({account_no}) credit and debit are both NOT 0')
    if credit != 0:
        return 'credit'
    else:
        return 'debit'


class ChartOfAccounts:
    def __init__(self):
        df = pd.read_excel('documents\\chart_of_accounts_mapping.xlsx')
        df['bs_is'] = df['bs_is'].astype('category')
        self.account_mapping = df
        self.accounts = {}
        self.trial_balances = None

    def get_account_mapping(self, account_no):
        map_row = self.account_mapping[account_no >= self.account_mapping['low']]
        map_row = map_row[account_no <= map_row['high']]
        if len(map_row) != 1:
            print(f'ERROR: more than one row match to account_no = {account_no}')
        return map_row

    def add_accounts(self, tb: pd.DataFrame):
        for i in range(len(tb)):
            row = tb.iloc[i]
            account_no = tb.index[i]
            description = row['description']
            debit = row['debit']
            credit = row['credit']
            dc = check_debit_credit(debit, credit, account_no)

            map_row = self.get_account_mapping(account_no)

            bs_is = map_row.iloc[0, 2]

            if account_no not in self.accounts.keys():
                account: Ledger = Ledger(account_no=account_no, description=description, debit_credit=dc, bs_is=bs_is)
                self.accounts[account_no] = account
                # print(f'adding: [{account_no}] {description}, {dc}, {bs_is}')
            else:
                account = self.accounts[account_no]
                if account.debit_credit != dc:
                    # raise Exception(f'ERROR: account_no={account_no} debit credit mismatch')
                    # print(f'warning: account_no={account_no} debit credit mismatch')
                    pass
                if account.bs_is != bs_is:
                    raise Exception(f'ERROR: account_no={account_no} bs_is mismatch')
                if account.description != description:
                    raise Exception(f'ERROR account_no={account_no} description mismatch')

    @timer
    def read_all_trial_balances(self):
        print('Finance model:')
        trial_balances = {}
        # ToDO Generalize the years. It should be a parameter
        years = [year for year in range(2017, 2024)]
        for year in years:
            print(f'year = {year}')
            filename = f"HazTrain TB.{year} by month GENAESIS Confidential.xlsx"
            path = f'documents\\trial_balances\\{filename}'
            xls = pd.ExcelFile(path)
            # wb = load_workbook(path)
            sheets = xls.sheet_names
            number_of_months = len(sheets)
            if number_of_months < 12:
                print(f'Too few months in {year}')
            for month_num in range(number_of_months):
                tb = read_trial_balance(xls, year, month_num)
                tb = clean_trial_balance(tb)
                self.add_accounts(tb)
                tb = collapse_trail_balance(tb, month_num + 1, year)
                recs = tb.transpose().to_dict(orient='index')
                trial_balances = trial_balances | recs
            # return
            # break
        # print(trial_balances)
        df = pd.DataFrame(trial_balances).T
        df = df.replace(float('nan'), 0)
        df = df.sort_index(axis=1)
        self.trial_balances = df

    def sorted_accounts(self):
        decorated = [(ledger.account_no, ledger) for ledger in list(self.accounts.values())]
        decorated.sort()
        undecorated = [leger for acc_id, leger in decorated]
        return undecorated

    def write_accounts(self):
        sorted_accounts = self.sorted_accounts()
        sorted_accounts = [ledger.to_dict() for ledger in sorted_accounts]
        df = pd.DataFrame(sorted_accounts)

        df.to_csv('chart of accounts.csv')
