from finance_model.chart_of_accounts import ChartOfAccounts
import pickle


def main():
    account = ChartOfAccounts()
    if False:
        account.read_all_trial_balances(2017, 2023)
        print(account.trial_balances)

        with open('charts.pickle', 'wb') as handle:
            pickle.dump(account, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # pickle.dump(account, "charts")
    else:
        with open('charts.pickle', 'rb') as handle:
            account = pickle.load(handle)
    account.plot_accounts(17)


if __name__ == '__main__':
    main()
