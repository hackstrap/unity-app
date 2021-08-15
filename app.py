import json
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request
from requests.api import get
from requests.exceptions import HTTPError
from rich.console import Console
console = Console()

from tables.revenue import tables_revenue
from tables.expenses import tables_expenses
from tables.users import tables_users
from tables.opex import tables_opex

from investor.investor import investor_investment_summary
from investor.investor import investor_startup_summary
from investor.investor import investor_investment_total
from investor.investor import investor_startups_invested
from investor.investor import investor_investor_startups
from investor.investor import investor_investments_month


#startups
from startups.tyke.test import test_rev
from startups.tyke.product import tables_product




base_url = "https://blink.hackstrap.com/"

PREFIX = "Bearer"


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token




app = Flask(__name__)

    
app.register_blueprint(tables_revenue)
app.register_blueprint(tables_expenses)
app.register_blueprint(tables_users)
app.register_blueprint(tables_opex)

app.register_blueprint(investor_investment_summary)
app.register_blueprint(investor_startup_summary)
app.register_blueprint(investor_investment_total)
app.register_blueprint(investor_startups_invested)
app.register_blueprint(investor_investor_startups)
app.register_blueprint(investor_investments_month)


app.register_blueprint(test_rev)
app.register_blueprint(tables_product)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/unity")
def unity():
    return "Welcome to Unity"


@app.route("/unity/v1")
def v1():
    return "List of v1 endpoints"


# FLASK_DEBUG=1 FLASK_APP=app.py flask run
# python3 -m flask run
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
