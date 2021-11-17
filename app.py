import json
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from requests.api import get
from requests.exceptions import HTTPError
from rich.console import Console

console = Console()

from api.api import api_market_overview
from api.file_upload import api_file_upload
from api.quickbooks_upload import api_quickbooks_upload, quickbooks_upload
from investor.investor import (
    investor_investment_summary,
    investor_investment_total,
    investor_investments_month,
    investor_investor_startups,
    investor_investor_startups_by_sectors,
    investor_startup_investment_total,
    investor_startup_investors,
    investor_startup_summary,
    investor_startups_invested,
)
from startups.tyke.product import tables_product

# startups
from startups.tyke.test import test_rev
from tables.expenses import tables_expenses
from tables.opex import tables_opex
from tables.revenue import tables_revenue
from tables.users import tables_users

base_url = "https://blink.hackstrap.com/"

PREFIX = "Bearer"


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token


app = Flask(__name__)
CORS(app)


app.register_blueprint(tables_revenue)
app.register_blueprint(tables_expenses)
app.register_blueprint(tables_users)
app.register_blueprint(tables_opex)

app.register_blueprint(investor_investment_summary)
app.register_blueprint(investor_startup_summary)
app.register_blueprint(investor_investment_total)
app.register_blueprint(investor_startup_investment_total)
app.register_blueprint(investor_startups_invested)
app.register_blueprint(investor_investor_startups)
app.register_blueprint(investor_investments_month)
app.register_blueprint(investor_investor_startups_by_sectors)
app.register_blueprint(investor_startup_investors)

app.register_blueprint(api_market_overview)
app.register_blueprint(api_file_upload)
app.register_blueprint(api_quickbooks_upload)

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


@app.errorhandler(404)
def page_not_found(error):
    return "Aborted with 404", 404


# FLASK_DEBUG=1 FLASK_APP=app.py flask run

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
