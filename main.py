from finance_model.chart_of_accounts import ChartOfAccounts


def main():
    account = ChartOfAccounts()
    account.read_all_trial_balances()

    print(account.trial_balances)


if __name__ == '__main__':
    main()
