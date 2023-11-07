import pandas as pd
from finance_model.account_description import AccountDescription
from finance_model.timer import timer
from finance_model.read_trial_balances import read_trial_balance, check_debit_credit, collapse_trail_balance
from itertools import compress
from finance_model.plot_financials import finance_plot
import pickle
from config import config
from finance_model.finance_enums import AccountLevel, IS_BS, CATEGORY, SUBCATEGORY, SUBCATEGORY2, DebitCredit
@timer
def unpickle_accounts():
    with open(config['coa_pickle'], 'rb') as handle:
        account = pickle.load(handle)
    return account


def pickle_accounts(account) -> None:
    # ToDo data structure fix
    # Also move this into class
    print(f'coa_pickle: {config["coa_pickle"]}')
    with open(config['coa_pickle'], 'wb') as handle:
        pickle.dump(account, handle, protocol=pickle.HIGHEST_PROTOCOL)


class ChartOfAccounts:
    """

    """
    def __init__(self):
        # account_map is a generic mapping of a range of account numbers to accounts.
        # It is only used to build the detailed account_map
        self.account_map: pd.DataFrame | None = None
        self.read_account_mapping()

        self.accounts: dict[str, AccountDescription] = {}
        self.trial_balances: pd.DataFrame  | None = None
        self.detailed_account_map = None

    def get_account_mapping(self, account_no: int) -> pd.DataFrame:
        """
        Given an account number, this method returns the corresponding row in the account_map
        :param account_no:
        :return: single row dataframe
        """
        map_row = self.account_map[account_no >= self.account_map['low']]
        map_row = map_row[account_no <= map_row['high']]
        if len(map_row) != 1:
            print(f'match error = {account_no}')
            print('maprow:')
            print(map_row)
            if len(map_row) == 0:
                raise RuntimeError(f"ERROR: no match found for account_no: {account_no}")
            else:
                raise RuntimeError(f"ERROR: more than one row match to account_no: {account_no}")
        return map_row

    def add_accounts(self, tb: pd.DataFrame) -> None:
        """
        add new accounts information to the accounts dict
        :param tb:
        :return:
        """
        for i in range(len(tb)):
            row = tb.iloc[i]
            account_no = tb.index[i]
            name = row['description']
            debit = row['debit']
            credit = row['credit']
            dc = check_debit_credit(debit, credit, account_no)
            try:
                map_row = self.get_account_mapping(account_no)
            except RuntimeError as e:
                e.add_note(f'error with: ({account_no}, {name})')
                raise
            bs_is = map_row.iloc[0, 2]

            if account_no not in self.accounts.keys():
                account: AccountDescription = AccountDescription(account_no, name, map_row)
                self.accounts[account_no] = account
                # print(f'adding: [{account_no}] {description}, {dc}, {bs_is}')
            else:
                # This is error checking to make certain that the trial balance accounts are consistent for all
                # periods
                account: AccountDescription = self.accounts[account_no]
                if account.debit_credit != dc:
                    # Note: some accounts can move between credit and debit month to month.
                    # This is handled when we collapse the trial balances in collapse_trail_balance
                    # it is not relevant whether they are a credit or a debit due to the collapse
                    pass
                if account.bs_is != bs_is:
                    raise Exception(f'ERROR: account_no={account_no} bs_is mismatch')
                if account.name != name:
                    raise Exception(f'ERROR account_no={account_no} description mismatch')

    def build_detailed_account_map(self) -> None:
        """
        Build a detailed account map containing all accounts

        This method builds a DataFrame that contains a rows for every account and the columns contain the
        cagetory, IS/BS information.
        :return: None
        """
        df_data = {AccountLevel.ACCOUNT_NO: [],
                   AccountLevel.IS_BS: [],
                   AccountLevel.NORMAL_BALANCE: [],
                   AccountLevel.CATEGORY: [],
                   AccountLevel.SUBCATEGORY: [],
                   AccountLevel.SUBCATEGORY2: [],
                   AccountLevel.ACCOUNT: [],
                   }
        # for account in self.accounts.values():
        for account_no in self.trial_balances.columns.to_list():
            account = self.accounts[account_no]
            acct_dict = account.to_dict()
            for k, v in df_data.items():
                v.append(acct_dict[k])
                df_data[k] = v
        df = pd.DataFrame(df_data)
        self.detailed_account_map = df

    def read_account_mapping(self) -> None:
        """
        Read in the account mapping file and stores it in self.account_map
        """
        df = pd.read_excel(config['coa_map'])
        df[AccountLevel.IS_BS] = pd.Categorical(df[AccountLevel.IS_BS], categories=[i for i in IS_BS])
        df[AccountLevel.CATEGORY] = pd.Categorical(df[AccountLevel.CATEGORY], categories=[i for i in CATEGORY])
        df[AccountLevel.SUBCATEGORY] = pd.Categorical(df[AccountLevel.SUBCATEGORY], categories=[i for i in SUBCATEGORY])
        df[AccountLevel.SUBCATEGORY2] = pd.Categorical(df[AccountLevel.SUBCATEGORY2],
                                                       categories=[i for i in SUBCATEGORY2])
        df[AccountLevel.NORMAL_BALANCE] = pd.Categorical(df[AccountLevel.NORMAL_BALANCE],
                                                         categories=[i for i in DebitCredit])
        rows = df[AccountLevel.SUBCATEGORY2].isna()
        df.loc[rows, AccountLevel.SUBCATEGORY2] = SUBCATEGORY2.NONE
        self.account_map = df

    @timer
    def read_all_trial_balances(self, start_year: int, end_year: int) -> None:
        print('Finance model:')
        trial_balances = {}
        years = [year for year in range(start_year, end_year + 1)]
        for year in years:
            print(f'year = {year}')
            filename = f"HazTrain TB.{year} by month GENAESIS Confidential.xlsx"
            path = f'{config["tb_dir"]}/{filename}'
            xls = pd.ExcelFile(path)
            # wb = load_workbook(path)
            sheets = xls.sheet_names
            number_of_months = len(sheets)
            if number_of_months < 12:
                print(f'Too few months in year {year}')
            for month_num in range(number_of_months):
                tb = read_trial_balance(xls, year, month_num)
                self.add_accounts(tb)
                collapsed_tb = collapse_trail_balance(tb, month_num + 1, year)
                recs = collapsed_tb.transpose().to_dict(orient='index')
                trial_balances = trial_balances | recs
        df = pd.DataFrame(trial_balances).T
        df = df.replace(float('nan'), 0)
        df = df.sort_index(axis=1)
        self.trial_balances = df

        self.build_detailed_account_map()

    def sorted_accounts(self) -> list[AccountDescription]:
        """
        Return the list of accounts sorted by account number.
        :return: List of accounts in numerical order
        """
        return sorted(self.accounts.values(), key=lambda x: x.account_no)

    def write_accounts(self) -> None:
        """
        Write the accounts to a csv file.
        :return:
        """
        sorted_accounts = self.sorted_accounts()
        sorted_accounts = [ledger.to_dict() for ledger in sorted_accounts]
        df = pd.DataFrame(sorted_accounts)
        print(f'coa_csv: {config["coa_csv"]}')
        # ToDo data structure fix
        df.to_csv(config['coa_csv'])

    @timer
    def get_data_to_plot(self, level, filter_value, group_by, yearly=False):
        print(f'get_data_to_plot {level}')
        print(f'level = {level}')
        tb = self.trial_balances.copy()
        if yearly:
            tb['year'] = [date[:4] for date in tb.index]
            grp = tb.groupby('year')
            # Choose the last of each grouping. This works because the data is cumulative
            tb = grp.tail(1).iloc[:, :-1]
        tb = tb.T

        tb['account_no'] = tb.index
        tb = tb.merge(self.detailed_account_map, how='left', on='account_no')

        rows = tb[level] == filter_value
        filtered_tb = tb[rows]

        label = "error bad label"
        # print(f'rows = {rows}')
        # print(f'filtered_tb = {filtered_tb}')
        # print(f'len(filtered_tb) = {len(filtered_tb)}')

        if len(filtered_tb) == 0:
            raise KeyError(f'no rows found for: {filter_value}')
        if len(filtered_tb) > 0:
            val = filtered_tb.iloc[0, -5:]
            pos = val.index.to_list().index(level)
            items = [val[item] for item in val.index]
            items = items[:pos]
            items.append(filter_value)
            items = pd.Series(items).drop_duplicates().to_list()
            label = " : ".join(items)
        group = filtered_tb.groupby(group_by)
        data = group.sum().iloc[:, :-5].T

        sub_data_names = data.columns.to_list()
        # data = data.iloc[:12]

        return data, label, sub_data_names

    @timer
    def plot_data(self, level, filter_value, group_by, binary=False, yearly=False):
        data, label, sub_data_names = self.get_data_to_plot(level, filter_value, group_by, yearly=yearly)
        return finance_plot(data, label, binary=binary, yearly=yearly), sub_data_names
