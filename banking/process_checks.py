import pandas as pd
import numpy as np
from config import config


def read_peachtree() -> pd.DataFrame:
    peachtree_file = pd.ExcelFile(config['peach_tree_checks'])

    peachtree_df = pd.read_excel(peachtree_file, dtype={"Check #": str,
                                                        "Cash Account": str})

    if peachtree_df.iloc[len(peachtree_df) - 1, 0] == "Total":
        peachtree_df = peachtree_df.iloc[:len(peachtree_df) - 2, :]
    print(peachtree_df.dtypes)
    peachtree_df.loc[peachtree_df["Amount"].isna(), "Amount"] = 0
    return peachtree_df


def read_pnc() -> pd.DataFrame:
    pnc_file = pd.ExcelFile(config['pnc_checks'])
    pnc_df = pd.read_excel(pnc_file)
    col = pnc_df.iloc[1, :]
    pnc_df.columns = col
    pnc_df = pnc_df.iloc[2:, :]
    pnc_df = pnc_df.drop(["Account Number", "Account Name", "Add'l Data", "Payee Name 2"], axis=1)
    pnc_df = pnc_df.set_index("Serial Number")

    pnc_df["Amount"] = pnc_df["Amount"].str[1:]
    pnc_df["Amount"] = pnc_df["Amount"].str.replace(",", "")
    pnc_df = pnc_df.astype({"Amount": float})
    pnc_df["Issue Date"] = pd.to_datetime(pnc_df["Issue Date"])
    pnc_df["Paid Date"] = pd.to_datetime(pnc_df["Paid Date"])
    pnc_df["Stop Effective Date"] = pd.to_datetime(pnc_df["Stop Effective Date"])
    pnc_df["Stop Expiry Date"] = pd.to_datetime(pnc_df["Stop Expiry Date"])

    issued_df = pnc_df.loc[pnc_df["Description"] == "Issued Check", :]
    paid_df = pnc_df.loc[pnc_df["Description"] == "Paid Check", ["Description", "Paid Date"]]
    # This will contain all of the checks that were issued before positive pay
    #    They will have an issue and a pay
    #    They will need to be fixed by merging pay info into the issue data
    #    This occurs because the check was issued and paid prior to positive pay
    # Also the checks that have been issued but not paid
    #    They will have an issue but no pay
    issue_join = issued_df.join(paid_df, how='left', rsuffix='_pd')

    paid_mask = issue_join["Description_pd"] == "Paid Check"
    issue_paid = issue_join.loc[paid_mask, :]
    issue_paid["Description"] = "Paid Check"
    issue_paid["Paid Date"] = issue_paid["Paid Date_pd"]
    issue_paid = issue_paid.loc[:, "Description":"Payee Name 1"]
    # print("Index:")
    # print(issue_paid.index)
    print("Issue Paid:")
    print(issue_paid)
    # issue_not_paid = issue_join.loc[issue_join["Description_pd"] != "Paid Check", :]
    issue_not_paid = issue_join.loc[paid_mask == False, "Description":"Payee Name 1"]
    paid_join = pnc_df.loc[pnc_df["Description"] == "Paid Check"].join(issued_df.loc[:, ["Description"]], how='left',
                                                                       rsuffix="_is")
    paid_join = paid_join.loc[paid_join["Description_is"] != "Issued Check","Description":"Payee Name 1"]
    # rjoin_df = issued_df.join(paid_df, how='right', rsuffix='_pd')
    # print("Join df")
    print("Not paid")
    print(issue_not_paid)
    # print("Paid Join")
    # print(paid_join)
    # "Issued Check"
    # "Paid Check"
    # "Stop Payment"
    # "Issued Check - VOID"

    # gg = pnc_df.loc[:, "Amount"]
    # print(f"gg ={gg}")
    # print(pnc_df.dtypes)
    return pnc_df


def process_checks(peachtree_df: pd.DataFrame) -> pd.DataFrame:
    # Note: void checks may be in the dataframe twice.
    # The first time they will look like normal checks
    # The second time the check number will end with a V. This indicates that the check should be voided

    # Get the voided checks and store them in a dataframe
    # Note there are edge cases where this won't work
    # ToDo Look into fixing the edge case
    void_mask = peachtree_df["Check #"].str.endswith("V")

    void_df = pd.DataFrame({'Check #': peachtree_df.loc[void_mask, "Check #"].str.rstrip("V"),
                            'Void': True,
                            'Void Date': peachtree_df.loc[void_mask, "Date"]
                            })
    # Merge the dataframe back into the original. This will add two columns void (bool) and
    # Void Date: which is the date of the voided check.
    merged_df = pd.merge(peachtree_df, void_df, how='left')
    merged_df.loc[merged_df['Void'].isna(), 'Void'] = False

    # This is kind of a hack. The checks all have string length of 5 so this will have the effect of
    # Stripping out the online payments as well as the voided checks
    check_mask = merged_df["Check #"].str.len() == 5
    check_df = merged_df[check_mask]

    # When a check is voided but never issues the Payee will be set to VOID and the amount will be
    # set to zero. This code correctly voids these checks.
    void_mask = check_df["Payee"] == "VOID"
    check_df.loc[void_mask, "Amount"] = 0
    check_df.loc[void_mask, "Void"] = True
    check_df.loc[void_mask, "Void Date"] = check_df.loc[void_mask, "Date"]

    # good_check_mask = check_df["Void"] == False
    # good_check_df = check_df[good_check_mask]

    return check_df


def write_issue_void(check_df: pd.DataFrame) -> None:
    # ToDo fix the account_number hack
    account_number = '5559464829'
    with open(f'{config['processed_dir']}/ISSUEVOIDFW.txt', 'w') as f:
        for index, check in check_df.iterrows():
            if check["Void"]:
                action = "V"
            else:
                action = "I"
            check_str = f'{account_number}{check["Check #"]:0>10}{check["Amount"]:11.2f}{check["Date"].month:02d}{check["Date"].day:02d}{check["Date"].year}{" ":<15}{check["Payee"]:<50}{" ":<50}{action}'
            f.write(check_str + '\n')
