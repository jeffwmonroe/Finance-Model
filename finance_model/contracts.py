import pandas as pd
from datetime import datetime
from finance_model.plot_financials import finance_plot
import math

class Contracts:
    def __init__(self):
        self.contracts = None
        self.contracts_yearly = None
        self.spend = None

    def read_contracts(self):
        df = pd.read_excel('documents/HazTrain Pipeline.xlsx',
                           sheet_name='backlog',
                           dtype={'pk': int},
                           )
        df = df.set_index('pk')
        self.contracts = df.iloc[:, :18]
        self.contracts_yearly = df.iloc[:, 20:30]
        self.contracts_yearly = self.contracts_yearly.fillna(0)

    def calculate_backlog_spend(self):
        dates = []
        data = {}
        for cont in self.contracts.index:
            data[cont] = []
        for year in range(2023, 2030):
            # data['years'] += [year] * 12
            # data['months'] += [month + 1 for month in range(12)]
            dates += [datetime(year=year, month=month + 1, day=1) for month in range(12)]
            for cont in self.contracts.index:
                start = self.contracts.loc[cont, 'start_date']
                end = self.contracts.loc[cont, 'end_date']
                yearly_spend = self.contracts_yearly.loc[cont, year]
                if end.year == year:
                    c_months = end.month
                    spend = [yearly_spend / end.month] * end.month
                    spend += [0.0] * (12 - end.month)
                elif end.year > year:
                    spend = [yearly_spend / 12] * 12
                else:
                    spend = [0.0] * 12
                if start.year > year:
                    spend = [0.0] * 12
                elif start.year == year:
                    spend = [0.0] * (start.month - 1)
                    months = 12 - start.month + 1
                    spend += [yearly_spend / months] * months
                data[cont] += spend

        self.spend = pd.DataFrame(data, index=dates)
        # self.spend.set_index('date')

    def get_data_to_plot(self, yearly=False, start_date=None):
        df = self.spend
        if start_date is None:
            df['year'] = df.index.map(lambda date: datetime(year=date.year, month=1, day=1))
        else:
            df['year'] = df.index.map(
                lambda date: datetime(year=2023 + math.floor((date - start_date).days / 365.2425), month=9, day=1))

        if yearly:
            group = df.groupby('year')
            yearly = group.sum()
            return yearly

        return df

    def plot_data(self, binary=False, yearly=False, start_date=None):
        df = self.get_data_to_plot(yearly=yearly, start_date=start_date)
        return finance_plot(df, "Spend", binary=binary, yearly=yearly)
