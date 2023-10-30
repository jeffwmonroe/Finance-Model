import pandas as pd
from finance_model.ledger import Ledger
from finance_model.timer import timer
from finance_model.read_trial_balances import read_trial_balance, check_debit_credit, collapse_trail_balance
from itertools import compress
from finance_model.plot_financials import finance_plot
import pickle


@timer
def unpickle_accounts():
    with open('charts.pickle', 'rb') as handle:
        account = pickle.load(handle)
    return account


def pickle_accounts(account) -> None:
    with open('charts.pickle', 'wb') as handle:
        pickle.dump(account, handle, protocol=pickle.HIGHEST_PROTOCOL)


class ChartOfAccounts:
    def __init__(self):
        # account_mapping is a generic mapping of a range of account numbers to accounts.
        # It is only used to build the detailed account_mapping
        self.account_mapping: pd.Dataframe = None
        self.read_account_mapping()

        self.accounts: dict[str, Ledger] = {}
        self.trial_balances: pd.DataFrame = None
        self.detailed_account_mapping = None

    def get_account_mapping(self, account_no: int) -> pd.DataFrame:
        map_row = self.account_mapping[account_no >= self.account_mapping['low']]
        map_row = map_row[account_no <= map_row['high']]
        if len(map_row) != 1:
            print(f'ERROR: more than one row match to account_no = {account_no}')
        return map_row

    def add_accounts(self, tb: pd.DataFrame) -> None:
        for i in range(len(tb)):
            row = tb.iloc[i]
            account_no = tb.index[i]
            description = row['description']
            debit = row['debit']
            credit = row['credit']
            dc = check_debit_credit(debit, credit, account_no)

            map_row = self.get_account_mapping(account_no)

            bs_is = map_row.iloc[0, 2]

            if account_no not in self.accounts.keys():
                account: Ledger = Ledger(account_no=account_no, description=description, debit_credit=dc, bs_is=bs_is)
                self.accounts[account_no] = account
                # print(f'adding: [{account_no}] {description}, {dc}, {bs_is}')
            else:
                # This is error checking to make certain that the trial balance accounts are consistent for all
                # periods
                account: Ledger = self.accounts[account_no]
                if account.debit_credit != dc:
                    # Note: some accounts can move between credit and debit month to month.
                    # This is handled when we collapse the trial balances in collapse_trail_balance
                    # it is not relevant whether they are a credit or a debit due to the collapse
                    pass
                if account.bs_is != bs_is:
                    raise Exception(f'ERROR: account_no={account_no} bs_is mismatch')
                if account.description != description:
                    raise Exception(f'ERROR account_no={account_no} description mismatch')

    def build_detailed_account_mapping(self) -> None:
        cols = [col for col in self.trial_balances.columns]
        blanks = [None] * len(cols)
        df_data = {'account_no': cols,
                   'bs_is': blanks,
                   'category': blanks,
                   'sub_category': blanks,
                   'sub_account': blanks,
                   'account': blanks}
        df = pd.DataFrame(df_data)
        for i in range(len(cols)):
            account_no = cols[i]
            row = self.get_account_mapping(account_no)
            df.iloc[i, 2:5] = row.iloc[0, 3:6]
            df.iloc[i, 5] = self.accounts[account_no].description
            df.iloc[i, 1] = self.accounts[account_no].bs_is
        self.detailed_account_mapping = df

    def read_account_mapping(self) -> None:
        """
        Read in the account mapping file and stores it in self.account_mapping
        """
        df = pd.read_excel('documents\\chart_of_accounts_mapping.xlsx')
        df['bs_is'] = df['bs_is'].astype('category')
        self.account_mapping = df

        rows = self.account_mapping.loc[:, 'sub_category'].isnull()
        self.account_mapping.loc[rows, 'sub_category'] = self.account_mapping.loc[rows, 'category']
        rows = self.account_mapping.loc[:, 'sub_account'].isnull()
        self.account_mapping.loc[rows, 'sub_account'] = self.account_mapping.loc[rows, 'sub_category']

    @timer
    def read_all_trial_balances(self, start_year: int, end_year: int) -> None:
        print('Finance model:')
        trial_balances = {}
        years = [year for year in range(start_year, end_year + 1)]
        for year in years:
            print(f'year = {year}')
            filename = f"HazTrain TB.{year} by month GENAESIS Confidential.xlsx"
            path = f'documents\\trial_balances\\{filename}'
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


        self.build_detailed_account_mapping()

    def sorted_accounts(self):
        decorated = [(ledger.account_no, ledger) for ledger in list(self.accounts.values())]
        decorated.sort()
        undecorated = [leger for acc_id, leger in decorated]
        return undecorated

    def write_accounts(self):
        sorted_accounts = self.sorted_accounts()
        sorted_accounts = [ledger.to_dict() for ledger in sorted_accounts]
        df = pd.DataFrame(sorted_accounts)

        df.to_csv('chart of accounts.csv')

    def sub_account_cols(self, sub_account):
        map_row = self.account_mapping.iloc[sub_account]
        columns = self.trial_balances.columns.to_list()
        low = columns >= map_row['low']
        high = columns <= map_row['high']
        match = low & high
        match_cols = list(compress(columns, match))

        return match_cols

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
        tb = tb.merge(self.detailed_account_mapping, how='left', on='account_no')

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

    def get_data_rows(self, level, filter, yearly=False):
        tb = self.trial_balances.copy()
        if yearly:
            tb['year'] = [date[:4] for date in tb.index]
            grp = tb.groupby('year')
            # Choose the last of each grouping. This works because the data is cumulative
            tb = grp.tail(1).iloc[:, :-1]
        tb = tb.T

        tb['account_no'] = tb.index
        tb = tb.merge(self.detailed_account_mapping, how='left', on='account_no')

        rows = [item in filter for item in tb[level]]
        filtered_tb = tb[rows]
        filtered_tb = filtered_tb.set_index('account_no')
        columns = filtered_tb.columns[-5:].to_list() + filtered_tb.columns[:-5].to_list()
        filtered_tb = filtered_tb.loc[:, columns]
        return filtered_tb

    @timer
    def plot_data(self, level, filter_value, group_by, binary=False, yearly=False):
        data, label, sub_data_names = self.get_data_to_plot(level, filter_value, group_by, yearly=yearly)
        return finance_plot(data, label, binary=binary, yearly=yearly), sub_data_names
