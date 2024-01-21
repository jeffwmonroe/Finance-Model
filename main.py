from finance_model import ChartOfAccounts, unpickle_accounts, pickle_accounts, clear_pickle
from finance_model import AccountLevel, IS_BS, FinNode
from collections import OrderedDict, deque
import pickle
from config import config
import click
import pandas as pd
from banking import Check
from banking import read_peachtree, process_checks, write_issue_void
import datetime

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
def clear():
    clear_pickle()


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
        print(f'cat = {cat}')
        catlist = deque(cat)
        top.insert_children(catlist, df, max_depth)

    top.print()


@cli.command()
@click.option("-c", "--last_check", )
def checks(last_check: str) -> None:
    peachtree_df = read_peachtree()
    print(peachtree_df)
    check_df = process_checks(peachtree_df)
    if last_check is not None:
        check_mask = check_df["Check #"] > last_check
        check_df = check_df[check_mask]
        print(check_df)
    write_issue_void(check_df)


def old_check_code() -> None:
    print(f"Checks: {config['peach_tree_checks']}")
    peachtree_df = pd.ExcelFile(config['peach_tree_checks'])

    peachtree_df = pd.read_excel(peachtree_df, dtype={"Check #": str,
                                                      "Cash Account": str})
    peachtree_df = peachtree_df.iloc[:len(peachtree_df) - 2, :]
    print(peachtree_df.dtypes)

    pnc_df = pd.read_csv(config['pnc_checks'],
                         dtype={"Serial Number": str,
                                "Amount": str,
                                "Account Number": str},
                         parse_dates=['Issue Date', 'Paid Date', 'Stop Effective Date', 'Stop Expiry Date'])
    pnc_df['Amount'] = pnc_df['Amount'].str.replace('$', '')
    pnc_df['Amount'] = pnc_df['Amount'].str.replace(',', '')
    pnc_df['Amount'] = pnc_df['Amount'].astype('float')
    pnc_df = pnc_df.rename(columns={"Amount": "PNC Amount"})
    print(pnc_df.dtypes)

    merged_df = peachtree_df.merge(pnc_df, left_on="Check #", right_on="Serial Number", how='left')
    print(merged_df)
    checks = {check[1]["Check #"]: Check(check[1]) for check in peachtree_df.iterrows()}

    print("checks:")
    print(pnc_df.columns)

    merged_df.to_excel(config['check_output'])

def main():
    cli()


if __name__ == '__main__':
    main()
