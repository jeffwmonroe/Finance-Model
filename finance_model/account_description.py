from finance_model.finance_enums import IS_BS, AccountLevel
import pandas as pd


class AccountDescription:
    def __init__(self, account_no: int, name: str, account_map: pd.DataFrame) -> None:
        self.account_no: int = account_no
        self.name: str = name
        self.debit_credit: str = "none"
        row = account_map.index[0]
        self.bs_is: IS_BS = account_map.loc[row, AccountLevel.IS_BS]
        self.category = account_map.loc[row, AccountLevel.CATEGORY]
        self.subcategory = account_map.loc[row, AccountLevel.SUBCATEGORY]
        self.subcategory2 = account_map.loc[row, AccountLevel.SUBCATEGORY2]
        self.normal_balance = account_map.loc[row, AccountLevel.NORMAL_BALANCE]

    def __repr__(self) -> str:
        return f'AccountDescription: ({self.account_no}, {self.name}, {self.debit_credit}, {self.bs_is})'

    def to_dict(self) -> dict[AccountLevel, str | int]:
        return {AccountLevel.ACCOUNT_NO: self.account_no,
                AccountLevel.IS_BS: self.bs_is,
                AccountLevel.NORMAL_BALANCE: self.normal_balance,
                AccountLevel.CATEGORY: self.category,
                AccountLevel.SUBCATEGORY: self.subcategory,
                AccountLevel.SUBCATEGORY2: self.subcategory2,
                AccountLevel.ACCOUNT: self.name,
                }
