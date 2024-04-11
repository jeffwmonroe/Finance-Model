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


def process_pnc_initial(pnc_df: pd.DataFrame):
    #########################################
    # In the initial data pull from PNC a check will sometimes be listed two times. This is for the
    # Checks that were processed before positive pay. The first instance will be the Issued Check and
    # the second instance will be the Paid Check.  The Paid check row will have the positive pay information.
    # The following code finds the duplicates, keeps the positive pay information, but then removes the
    # duplicate rows.
    issued_df = pnc_df.loc[pnc_df["Description"] == "Issued Check", :]
    paid_df = pnc_df.loc[pnc_df["Description"] == "Paid Check", ["Description", "Paid Date"]]
    double_entry_df = issued_df.join(paid_df, how='inner', rsuffix='_pd')
    double_entry_df["Description"] = "Paid Check"
    double_entry_df["Paid Date"] = double_entry_df["Paid Date_pd"]
    double_entry_df = double_entry_df.loc[:, "Description":"Payee Name 1"]

    single_entry_df = pnc_df[~pnc_df.index.duplicated(keep=False)]

    processed_df = pd.concat([single_entry_df, double_entry_df]).sort_index()
    # print(processed_df)
    return processed_df


def pnc_update_check_status(pnc_df, update_df, new_status):
    update_df = update_df.drop_duplicates()
    return_value = pnc_df.copy()
    update_df = update_df.loc[update_df["Description"] == new_status, ["Description", "Paid Date"]]
    merged_df = return_value.join(update_df, how='left', rsuffix='_pd')

    assert len(return_value.index) == len(merged_df.index)

    update_mask = (~merged_df['Description_pd'].isna()) & (merged_df['Description'] == 'Issued Check')
    return_value.loc[update_mask, "Paid Date"] = merged_df.loc[update_mask, "Paid Date_pd"]
    return_value.loc[update_mask, "Description"] = new_status

    return return_value


def process_pnc_update(pnc_df, update_df):
    return_value = pnc_update_check_status(pnc_df, update_df, "Paid Check")
    return_value = pnc_update_check_status(return_value, update_df, "Issued Check - VOID")
    return_value = pnc_update_check_status(return_value, update_df, "Stop Payment")

    issued_df = update_df.loc[update_df["Description"] == "Issued Check", :]
    merged_df = issued_df.join(return_value.loc[:, ["Description", "Payee Name 1"]], how='left', rsuffix='_pd')
    merged_df = merged_df.loc[merged_df['Description_pd'].isna(), "Description":"Payee Name 1"]
    return_value = pd.concat([return_value, merged_df]).sort_index()
    return return_value


def read_pnc(pnc_file) -> pd.DataFrame:
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
    return pnc_df


def dummy():
    # print("Index:")
    # print(issue_paid.index)
    print("Issue Paid:")
    # print(issue_paid)
    # issue_not_paid = issue_join.loc[issue_join["Description_pd"] != "Paid Check", :]
    paid_join = pnc_df.loc[pnc_df["Description"] == "Paid Check"].join(issued_df.loc[:, ["Description"]], how='left',
                                                                       rsuffix="_is")
    paid_join = paid_join.loc[paid_join["Description_is"] != "Issued Check", "Description":"Payee Name 1"]
    # rjoin_df = issued_df.join(paid_df, how='right', rsuffix='_pd')
    # print("Join df")
    print("Not paid")
    # print(issue_not_paid)
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
