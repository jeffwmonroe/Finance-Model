import requests
from flask import render_template
from app import app
from app.dependencies import get_chart_of_accounts
from app.forms import AccountControl
from finance_model import ChartOfAccounts


# from config import config

@app.route("/", methods=["GET", "POST"])
def home_page():
    accounts: ChartOfAccounts = get_chart_of_accounts()
    print(f'home_page')
    form = AccountControl()
    chart_number = 0
    plot_level = 0

    if form.validate_on_submit():
        chart_number = form.chart_number.data
        print(f'chart_number = {chart_number}')
        if form.increase.data:
            chart_number += 1
        if form.decrease.data:
            chart_number -= 1
        if chart_number < 0:
            chart_number = 0
        if form.decrease.data or form.increase.data:
            form.chart_number.data = chart_number
            form.chart_number.raw_data = [f'{chart_number}']
        plot_level = int(form.level.data)
        print(f'plot_level = {plot_level}')
    else:
        form.chart_number.data = chart_number
        form.level.data = plot_level

    categories = accounts.account_mapping.columns.to_list()[2:]
    categories.append('account')
    print(f'categgories = {categories}')

    group_level = plot_level + 1
    level = categories[plot_level]
    group_by = categories[group_level]
    levels = accounts.account_mapping[level].unique()
    print(f'levels = {levels} : {len(levels)}')
    if chart_number >= len(levels):
        chart_number -= 1
        form.chart_number.data = chart_number
        form.chart_number.raw_data = [f'{chart_number}']
    item = levels[chart_number]

    data, sub_data_names = accounts.plot_data(level, item, group_by, binary=True, yearly=True)
    print(f'sub_data_names = {sub_data_names}')
    # return f"<img src='data:image/png;base64,{data}'/>"
    return render_template("home.html", chart=data, form=form)
