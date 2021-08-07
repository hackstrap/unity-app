import json
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from flask import Blueprint, jsonify, request
from requests.api import get
from requests.exceptions import HTTPError
from rich.console import Console
console = Console()

base_url = "https://blink.hackstrap.com/"

PREFIX = "Bearer"


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token

investor_investment_summary = Blueprint("investor_investment_summary", __name__)

@investor_investment_summary.route("/unity/v1/investor/investment_summary", methods=["GET"])
def investment_summary():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    result = requests.get(
        base_url
        + "v1/portfolio?"
        + "page={}&page_size={}&investor_id={}".format(page, page_size, investor_id),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )
    if result.text == "[]":
        return jsonify([])

    else:
        data = json.loads(result.text)

        data = data[0]
        data = data["investment_summary"][0]
        # data = data['investment_summary']
        return data


investor_investment_total = Blueprint("investor_investment_total", __name__)

@investor_investment_total.route("/unity/v1/investor/investment_total", methods=["GET"])
def investment_total():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    year = request.args.get("year")
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    if year == None:
        result = requests.get(
            base_url
            + "v1/investment?"
            + "page={}&page_size={}&investor_id={}".format(
                page, page_size, investor_id
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

    else:
        result = requests.get(
            base_url
            + "v1/investment?"
            + "page={}&page_size={}&investor_id={}&year={}".format(
                page, page_size, investor_id, year
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

    if result.text == "[]":
        return jsonify([])

    else:
        data = json.loads(result.text)
        data = pd.DataFrame(data)
        data = pd.DataFrame(data.groupby(by=["investor_id"])["amount"].sum())
        data = data.to_dict()
        data = json.dumps(data)
        return data

