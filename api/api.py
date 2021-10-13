import datetime
import json
import math
from datetime import datetime

import arrow as arw
import numpy as np
import pandas as pd
import pytz
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin
from requests.api import get
from requests.exceptions import HTTPError
from rich.console import Console

console = Console()


from utils.default_data import default_portfolio

base_url = "https://blink.hackstrap.com/"

local_url = "http://127.0.0.1:5000/"

PREFIX = "Bearer"


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token


api_market_overview = Blueprint("api_market_overview", __name__)
CORS(api_market_overview)


@api_market_overview.route(
    "/unity/v1/api/market_overview", methods=["GET"]
)
def market_overview():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    market_id = request.args.get("market_id")
    country_id = request.args.get("country_id")
    header = request.headers.get("Authorization")
    access_token = get_token(header)
    now_year_India = arw.now("Asia/Kolkata").year
    now_month_India = arw.now("Asia/Kolkata").month

    market_overview_result = requests.get(
        base_url
        + "v1/market_overview?"
        + "page={}&page_size={}&market_id={}".format(page, page_size, market_id),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )
        
    if market_overview_result.text == "[]":
        return jsonify([])
    
    else:
        
        data = json.loads(market_overview_result.text)
        data = json.dumps(data[0]["countries"]["{}".format(country_id.lower())])
        
        return data