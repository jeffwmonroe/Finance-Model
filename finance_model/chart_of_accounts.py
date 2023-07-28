import pandas as pd
from finance_model.ledger import Ledger


class ChartOfAccounts:
    def __init__(self):
        df = pd.read_excel('documents\\chart_of_accounts_mapping.xlsx')
        df['bs_is'] = df['bs_is'].astype('category')
        self.account_mapping = df
        self.accounts = {}

    def add_accounts(self, tb: pd.DataFrame):
        for i in range(len(tb)):
            row = tb.iloc[i]
            account_no = tb.index[i]
            description = row['description']
            debit = row['debit']
            credit = row['credit']
            if debit == 0 and credit == 0:
                raise Exception(f'({account_no}) credit and debit are both 0')
            if debit != 0 and credit != 0:
                raise Exception(f'({account_no}) credit and debit are both NOT 0')
            if credit != 0:
                dc = 'credit'
            else:
                dc = 'debit'
            map_row = self.account_mapping[account_no >= self.account_mapping['low']]
            map_row = map_row[account_no <= map_row['high']]
            if len(map_row) != 1:
                print(f'ERROR: more than one row match to account_no = {account_no}')
            bs_is = map_row.iloc[0, 2]
            if debit < 0:
                Exception(f"ERROR: {account_no} debit is a negative number")
            if credit < 0:
                Exception(f"ERROR: {account_no} credit is a negative number")
            if account_no not in self.accounts.keys():
                account: Ledger = Ledger(account_no=account_no, description=description, debit_credit=dc, bs_is=bs_is)
                self.accounts[account_no] = account
                print(f'adding: [{account_no}] {description}, {dc}, {bs_is}')
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

            # print(f'row[{account_no}]= {row}')

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
