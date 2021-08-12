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


investor_startups_invested = Blueprint("investor_startups_invested", __name__)

@investor_startups_invested.route("/unity/v1/investor/startups_invested", methods=["GET"])
def startups_invested():
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
        data = data.groupby(by=["investor_id"])["startup_id"].unique()
        data = data.to_json(orient="index")
        return data


investor_investor_startups = Blueprint("investor_investor_startups", __name__)

@investor_investor_startups.route("/unity/v1/investor/investor_startups", methods=["GET"])
def investor_startups():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    year = request.args.get("year")
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    result = requests.get(
        base_url
        + "v1/investment?"
        + "page={}&page_size={}&investor_id={}".format(page, page_size, investor_id),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )

    startups = requests.get(
        base_url + "v1/startup?" + "page={}&page_size={}".format(page, page_size),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )


    if result.text == "[]":
        return jsonify([])
    
    if startups.text == "[]":
        return jsonify([])

    else:
        data = json.loads(result.text)
        data = pd.DataFrame(data)

        startups = json.loads(startups.text)
        startups = pd.DataFrame(startups)
        startups = startups[["startup_name", "startup_id"]]

        startups_total = pd.merge(startups, data, on="startup_id")
        startups_array = startups_total[["investor_id", "startup_name", "startup_id"]]

        startups_array = startups_array.groupby(by=["investor_id"])["startup_id"].unique()

        data = pd.DataFrame(startups_array["{}".format(investor_id)], columns=["startup_id"])
        data = pd.merge(data, startups, on="startup_id")
        data = data.to_json(orient="index")

        return data


investor_investments_month = Blueprint("investor_investments_month", __name__)

@investor_investments_month.route("/unity/v1/investor/investments_month", methods=["GET"])
def investments_month():
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
        data = data.groupby(by=["investor_id", "year", "month"])["amount"].sum()
        data = data.reset_index().to_json(orient="records")
        return data