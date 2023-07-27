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
            id = tb.index[i]
            description = row['description']
            debit = row['debit']
            credit = row['credit']
            if debit == 0 and credit == 0:
                raise Exception(f'({id}) credit and debit are both 0')
            if debit != 0 and credit != 0:
                raise Exception(f'({id}) credit and debit are both NOT 0')
            if credit != 0:
                dc = 'credit'
            else:
                dc = 'debit'
            map_row = self.account_mapping[id >= self.account_mapping['low']]
            map_row = map_row[id <= map_row['high']]
            if len(map_row) != 1:
                print(f'ERROR: more than one row match to id = {id}')
            bs_is = map_row.iloc[0, 2]
            if debit < 0:
                Exception(f"ERROR: {id} debit is a negative number")
            if credit < 0:
                Exception(f"ERROR: {id} credit is a negative number")
            if id not in self.accounts.keys():
                account: Ledger = Ledger(id=id, description=description, debit_credit=dc, bs_is=bs_is)
                self.accounts[id] = account
                print(f'adding: [{id}] {description}, {dc}, {bs_is}')
            else:
                account = self.accounts[id]
                if account.debit_credit != dc:
                    # raise Exception(f'ERROR: id={id} debit credit mismatch')
                    # print(f'warning: id={id} debit credit mismatch')
                    pass
                if account.bs_is != bs_is:
                    raise Exception(f'ERROR: id={id} bs_is mismatch')
                if account.description != description:
                    raise Exception(f'ERROR id={id} description mismatch')

            # print(f'row[{id}]= {row}')

    def sorted_accounts(self):
        decorated = [(ledger.id, ledger) for ledger in list(self.accounts.values())]
        decorated.sort()
        undecorated = [leger for acc_id, leger in decorated]
        return undecorated

    def write_accounts(self):
        sorted_accounts = self.sorted_accounts()
        sorted_accounts = [ledger.to_dict() for ledger in sorted_accounts]
        df = pd.DataFrame(sorted_accounts)

        df.to_csv('chart of accounts.csv')
