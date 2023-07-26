import pandas as pd
from finance_model.ledger import Ledger

class ChartOfAccounts:
    def __init__(self):
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
            bs_is = "unknown"
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
