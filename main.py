from finance_model import ChartOfAccounts, unpickle_accounts, pickle_accounts, clear_pickle
from finance_model import AccountLevel, IS_BS, FinNode
from collections import OrderedDict, deque
import pickle
from config import config
import click
import pandas as pd
from banking import Check
from banking import read_peachtree, process_checks, write_issue_void, read_pnc, process_pnc_initial, process_pnc_update
import datetime


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
    print(peachtree_df)
    check_df = process_checks(peachtree_df)
    if last_check is not None:
        check_mask = check_df["Check #"] > last_check
        check_df = check_df[check_mask]
        print(check_df)
    write_issue_void(check_df)


@click.command()
def outstanding():
    """Calculate balance of outstanding checks"""
    print("Calculating the balance of outstanding checks!")
    peachtree_df = read_peachtree()
    # print(peachtree_df)
    pnc_file = pd.ExcelFile(config['pnc_checks'])
    pnc_df = read_pnc(pnc_file)
    pnc_df = process_pnc_initial(pnc_df)
    # print('-' * 50)
    # print('pnc DF after initial process')
    # print(pnc_df)

    update_files = ["pnc report 5 feb.xlsx", "pnc report 12 feb.xlsx", "pnc report 15 feb.xlsx",]
    # update_files = ["pnc report 5 feb.xlsx"]
    update_files = [f"{config['check_dir']}/{file}" for file in update_files]

    for file in update_files:
        update_df = read_pnc(file)
        print(f'file = {file}')
        pnc_df = process_pnc_update(pnc_df, update_df)
    print('-' * 70)
    print('final result')
    mask = (pnc_df["Description"] == "Issued Check")
    print(f'mask = {mask} {type(mask)}')

    print(pnc_df.loc[pnc_df["Description"] == "Issued Check", :])
    print(f'Outstanding Amount = ${pnc_df.loc[pnc_df["Description"] == "Issued Check", "Amount"].sum():,.2f}')
    pnc_df.to_excel(config['processed_check_output'])

    print(update_files)
bank.add_command(process)
bank.add_command(outstanding)


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
    pnc_df['Amount'] = pnc_df['Amount'].str.replace('$_', '')
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
    """Main function"""
    # finance()
    wacky()


if __name__ == '__main__':
    main()
