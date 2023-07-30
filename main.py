from finance_model import ChartOfAccounts, unpickle_accounts, pickle_accounts
import pickle


def main():
    if False:
        account = ChartOfAccounts()
        account.read_all_trial_balances(2017, 2023)
        print(account.trial_balances)

        pickle_accounts(account)
        # pickle.dump(account, "charts")
    else:
        account = unpickle_accounts()
    account.plot_accounts(17)


if __name__ == '__main__':
    main()
