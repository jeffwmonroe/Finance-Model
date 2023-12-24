import pandas as pd


class Check:
    def __init__(self, data: pd.Series):
        self.check_no = data["Check #"]
        self.date = data["Date"]
        self.payee = data["Payee"]
        self.cash_account = data["Cash Account"]
        self.amount = data["Amount"]

    def __str__(self):
        return f'{[self.check_no]}   {self.date.strftime("%m-%d-%Y")}  ({self.payee}):  {self.amount}'
