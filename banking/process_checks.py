import pandas as pd
import numpy as np
from config import config


def read_peachtree() -> pd.DataFrame:
    peachtree_df = pd.ExcelFile(config['peach_tree_checks'])

    peachtree_df = pd.read_excel(peachtree_df, dtype={"Check #": str,
                                                      "Cash Account": str})

    if peachtree_df.iloc[len(peachtree_df) - 1, 0] == "Total":
        peachtree_df = peachtree_df.iloc[:len(peachtree_df) - 2, :]
    print(peachtree_df.dtypes)
    peachtree_df.loc[peachtree_df["Amount"].isna(), "Amount"] = 0
    return peachtree_df


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
    # ToDo fis the account_number hack
    account_number = '5559464829'
    with open(f'{config['processed_dir']}/ISSUEVOIDFW.txt', 'w') as f:
        for index, check in check_df.iterrows():
            if check["Void"]:
                action = "V"
            else:
                action = "I"
            check_str = f'{account_number}{check["Check #"]:0>10}{check["Amount"]:11.2f}{check["Date"].month:02d}{check["Date"].day:02d}{check["Date"].year}{" ":<15}{check["Payee"]:<50}{" ":<50}{action}'
            f.write(check_str + '\n')
