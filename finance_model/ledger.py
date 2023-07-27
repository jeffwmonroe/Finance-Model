
class Ledger:
    def __init__(self, id=0, description="", debit_credit="", bs_is="unknownS"):
        self.id = id
        self.description = description
        self.debit_credit = debit_credit
        self.bs_is = bs_is

    def __repr__(self):
        return f'({self.id}, {self.description}, {self.debit_credit}, {self.bs_is})"'

    def to_dict(self):
        return {'id': self.id,
                'description': self.description,
                'debit_credit': self.debit_credit,
                'bs_is': self.bs_is
                }
