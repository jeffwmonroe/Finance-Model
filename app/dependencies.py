from finance_model import ChartOfAccounts, unpickle_accounts
from finance_model.timer import timer
import pickle

CHART_OF_ACCOUNTS = None


@timer
def get_chart_of_accounts():
    global CHART_OF_ACCOUNTS

    if CHART_OF_ACCOUNTS is None:
        CHART_OF_ACCOUNTS = unpickle_accounts()
    return CHART_OF_ACCOUNTS
