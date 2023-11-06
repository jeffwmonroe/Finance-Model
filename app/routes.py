import requests
from flask import render_template
from app import app
from app.dependencies import get_chart_of_accounts
from app.forms import AccountControl
from finance_model import ChartOfAccounts
from flask import request


# from config import config
def handle_increase_decrease(form, chart_number):
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

    # print(f'plot_level = {plot_level}')
    return chart_number


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/matplotlib_bar", methods=["GET", "POST"])
def matplotlib_bar():
    print('-' * 50)
    print(f'home page:  {request.method}')
    accounts: ChartOfAccounts = get_chart_of_accounts()
    form = AccountControl()
    chart_number: int = 0
    # plot_level is int level for accounts detail
    plot_level: int = 0
    yearly: bool = True

    # if form.validate_on_submit():
    if request.method == 'POST':
        print(f'validate_on_submit')
        plot_level = int(form.level.data)
        yearly = form.yearly.data
        chart_number = form.chart_number.data
        if form.submit.data:
            chart_number = 0
            form.chart_number.data = chart_number
            form.chart_number.raw_data = [f'{chart_number}']
        if form.category.data:
            pass
        else:
            chart_number = handle_increase_decrease(form, chart_number)
    else:
        print(f'default!')
        form.chart_number.data = chart_number
        form.level.data = plot_level
        form.yearly.data = yearly

    categories = accounts.account_map.columns.to_list()[2:]
    categories.append('account')
    print(f'categories = {categories}')

    group_level = plot_level + 1
    level = categories[plot_level]
    group_by = categories[group_level]
    level_names = accounts.account_map[level].unique()
    print(f'levels = {level_names} : {len(level_names)}')
    item = level_names[chart_number]

    data, sub_data_names = accounts.plot_data(level, item, group_by, binary=True, yearly=yearly)

    chs = [(name, name.upper()) for name in sub_data_names]
    chs_in_form = form.sub_categories.choices
    if chs == chs_in_form:
        print(f'choices stayed the same: {chs}')
    else:
        print(f'choices not same:')
        print(f'choices in form: {chs_in_form}')
    default = [name for name in sub_data_names]
    form.sub_categories.choices = chs
    form.sub_categories.data = default

    # form.sub_categories.size = len(chs)
    print(f'sub_data_names = {sub_data_names}')
    # return f"<img src='data:image/png;base64,{data}'/>"
    return render_template("matplotlib_bar.html", chart=data, form=form)
