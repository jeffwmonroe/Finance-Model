from finance_model import ChartOfAccounts, unpickle_accounts, pickle_accounts
from finance_model import AccountLevel, IS_BS, FinNode
from collections import OrderedDict, deque
import pickle
from config import config
import click


@click.group()
def cli():
    print('inside of cli')


@cli.command()
def read():
    print("read trial balances")
    account = ChartOfAccounts()
    account.read_all_trial_balances(2017, 2023)
    print(account.trial_balances)

    pickle_accounts(account)


@cli.command()
@click.option("-y", "--yearly", is_flag=True)
@click.option("-w", "--write_accounts", is_flag=True)
def balance(yearly, write_accounts):
    print("unpickling accounts")
    account = unpickle_accounts()

    if write_accounts:
        account.write_accounts()

    tb = account.trial_balances.copy()

    # yearly = True

    if yearly:
        tb['year'] = [date[:4] for date in tb.index]
        grp = tb.groupby('year')
        # Choose the last of each grouping. This works because the data is cumulative
        tb = grp.tail(1).iloc[:, :-1]

    # print('Trial Balances')
    # print(tb.T)

    tbt = tb.T

    tbt[AccountLevel.ACCOUNT_NO] = tbt.index
    tbt = tbt.merge(account.detailed_account_map, how='left', on=AccountLevel.ACCOUNT_NO)
    # print('Merged Trial Balances:')
    # print(tbt)

    tb2 = tbt[tbt[AccountLevel.IS_BS] == IS_BS.BS]
    # print('Filtered trial balances')
    # print(tb2)

    grp2 = tb2.groupby([AccountLevel.CATEGORY, AccountLevel.SUBCATEGORY, AccountLevel.SUBCATEGORY2], sort=False)
    # grp2
    max_depth = 4
    top = FinNode('BS', max_depth)
    for cat, df in grp2:
        # print(f'cat = {cat}')
        catlist = deque(cat)
        top.insert_children(catlist, df, max_depth)

    top.print()


def main():
    print('before cli')
    cli()
    print('after cli')


if __name__ == '__main__':
    main()
