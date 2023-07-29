from finance_model import ChartOfAccounts
from finance_model.timer import timer
import pickle
CHART_OF_ACCOUNTS = None

@timer
def get_chart_of_accounts():
    global CHART_OF_ACCOUNTS

    if CHART_OF_ACCOUNTS is None:
        CHART_OF_ACCOUNTS = ChartOfAccounts()
        account = ChartOfAccounts()
        with open('charts.pickle', 'rb') as handle:
            CHART_OF_ACCOUNTS = pickle.load(handle)
    return CHART_OF_ACCOUNTS
