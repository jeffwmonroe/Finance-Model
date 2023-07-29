from finance_model.chart_of_accounts import ChartOfAccounts


def main():
    account = ChartOfAccounts()
    account.read_all_trial_balances(2017, 2023)

    print(account.trial_balances)

    account.plot_accounts(17)


if __name__ == '__main__':
    main()
