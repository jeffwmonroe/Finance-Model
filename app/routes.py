import requests
from flask import render_template
from app import app
from app.dependencies import get_chart_of_accounts
from app.forms import AccountControl


# from config import config

@app.route("/", methods=["GET", "POST"])
def home_page():
    print(f'home_page')
    form = AccountControl()
    chart_number = 0
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
    else:
        form.chart_number.data = chart_number
    accounts = get_chart_of_accounts()
    data = accounts.plot_accounts(chart_number, binary=True)
    # return f"<img src='data:image/png;base64,{data}'/>"
    return render_template("home.html", chart=data, form=form)
