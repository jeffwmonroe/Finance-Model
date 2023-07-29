import os
from finance_model import ChartOfAccounts
from flask import Flask


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"


app = Flask(__name__)
app.config.from_object(Config)


from app import routes
