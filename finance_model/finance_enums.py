from enum import Enum


class AccountLevel(str, Enum):
    ACCOUNT_NO = "account no"
    IS_BS = "is_bs"
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    SUBCATEGORY2 = "subcategory2"
    ACCOUNT = "account"
    NORMAL_BALANCE = "normal balance"


class DebitCredit(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

    def __str__(self):
        return self.name


class IS_BS(str, Enum):
    BS = "bs"
    IS = "is"

    def __str__(self):
        return self.name


class CATEGORY(str, Enum):
    ASSETS = 'assets'
    LIABILITIES = 'liabilities'
    EQUITY = 'equity'
    REVENUE = 'revenue'
    COGS = 'cost of goods sold'
    OPERATING_EXPENSES = 'operating expenses'
    OTHER_EXPENSES = 'other expenses'
    OTHER_INCOME = 'other income'

    def __str__(self):
        return self.name


class SUBCATEGORY(str, Enum):
    CURRENT_ASSETS = 'current assets'
    LONG_TERM_ASSETS = 'long term assets'
    CURRENT_LIABILITIES = 'current liabilities'
    LONG_TERM_LIABILITIES = 'long term liabilities'
    STOCK = 'stock'
    DISTRIBUTIONS = 'distributions'
    OWNERS_EQUITY = 'owners equity'
    CONTRACT_REVENUE = 'contract revenue'
    OTHER_REVENUE = 'other revenue'
    DIRECT_LABOR = 'direct labor'
    SUBCONTRACTORS = 'subcontractors'
    OTHER_COSTS = 'other costs'
    FRINGE = 'fringe'
    FACILITIES = 'facilities'
    OVERHEAD = 'overhead'
    GNA = 'g&a'
    UNALLOWABLE = 'unallowable'

    def __str__(self):
        return self.name


class SUBCATEGORY2(str, Enum):
    CASH_AND_EQUIVALENTS = 'cash and equivalents'
    ACCOUNTS_RECEIVABLE = 'accounts receivable'
    PROPERTY_AND_EQUIPMENT = 'property and equipment'
    OTHER_ASSETS = 'other assets'
    ACCOUNTS_PAYABLE = 'accounts payable'
    ACCRUED_EXPENSES = 'accrued expenses'
    OTHER_CURRENT_LIABILITIES = 'other current liabilities'
    OTHER_LONG_TERM_LIABILITIES = 'other long term liabilities'
    NONE = 'none'

    def __str__(self):
        return self.name


type FIN_CATEGORY = CATEGORY | SUBCATEGORY | SUBCATEGORY2
