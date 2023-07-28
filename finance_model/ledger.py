
class Ledger:
    def __init__(self, account_no=0, description="", debit_credit="", bs_is="unknownS"):
        self.account_no: int = account_no
        self.description: str = description
        self.debit_credit: str = debit_credit
        self.bs_is: str = bs_is

    def __repr__(self):
        return f'({self.account_no}, {self.description}, {self.debit_credit}, {self.bs_is})"'

    def to_dict(self):
        return {'id': self.account_no,
                'description': self.description,
                'debit_credit': self.debit_credit,
                'bs_is': self.bs_is
                }
