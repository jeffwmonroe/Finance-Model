from finance_model import ChartOfAccounts, unpickle_accounts, pickle_accounts, clear_pickle
from finance_model import AccountLevel, IS_BS, FinNode
from collections import OrderedDict, deque
import pickle
from config import config
import click
import pandas as pd
from banking import Check, make_ach_payment
from banking import read_peachtree, process_checks, write_issue_void, calculate_outstanding_checks
import datetime
import os


@click.group()
def wacky():
    """Application for helping to manage company"""


@wacky.group()
def finance():
    """finance group of commands"""
    print('inside of cli')


@finance.command()
def read():
    print("read trial balances")
    account = ChartOfAccounts()
    account.read_all_trial_balances(2017, 2023)
    print(account.trial_balances)

    pickle_accounts(account)


@finance.command()
def clear():
    clear_pickle()


@finance.command()
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
        print(f'cat = {cat}')
        catlist = deque(cat)
        top.insert_children(catlist, df, max_depth)

    top.print()


@wacky.group()
def bank():
    """Bank group of commands"""
    pass


@click.command()
@click.option("-lc", "--last_check",
              default=None,
              help="the last check number sent to PNC")
def process(last_check: str) -> None:
    """Process checks from Peach Tree for use with Positive Pay"""
    peachtree_df = read_peachtree()
    print("Peachtree DF")
    print(peachtree_df)
    check_df = process_checks(peachtree_df)
    if last_check is not None:
        check_mask = check_df["Check #"] > last_check
        check_df = check_df[check_mask]
        print('-' * 30)
        print("Check DF")
        print(check_df)
    write_issue_void(check_df)


@click.command()
def outstanding():
    """Calculate balance of outstanding checks"""
    print("Calculating the balance of outstanding checks!")
    calculate_outstanding_checks()


@click.command()
@click.option("-d", "--effective_date",
              default=None,
              help="THe effective date for the payment")
def ach_payment(effective_date: str) -> None:
    print(f'Effective Date: {effective_date}')
    make_ach_payment(effective_date)


@click.command()
def test():
    print("Test")


bank.add_command(process)
bank.add_command(outstanding)
bank.add_command(ach_payment)
bank.add_command(test)

def main():
    """Main function"""
    # finance()
    wacky()


if __name__ == '__main__':
    main()
