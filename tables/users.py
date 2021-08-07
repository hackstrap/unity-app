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


tables_users = Blueprint("tables_users", __name__)

@tables_users.route("/unity/v1/users", methods=["GET"])

def users():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    startup_id = request.args.get("startup_id")
    year = request.args.get("year")
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    request_base_url = request.base_url

    try:
        result = requests.get(
            base_url
            + "v1/users?"
            + "page={}&page_size={}&startup_id={}&year={}".format(
                page, page_size, startup_id, year
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

        # If the response was successful, no Exception will be raised
        result.raise_for_status()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    else:
        print("Success!")
    result = requests.get(
        base_url
        + "v1/users?"
        + "page={}&page_size={}&startup_id={}&year={}".format(
            page, page_size, startup_id, year
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
        data["total_customers"] = (
        data["total_customers_at_beginning_of_month"]
        + data["total_new_customers_acquired"]
        - data["total_customers_churned"]
    )
        data["total_monthly_active_users_gr"] = (
        data["total_monthly_active_users"].pct_change().fillna(0).round(3) * 100
    )
        data["customer_churn_rate"] = (
        data["total_customers_churned"] / data["total_customers_at_beginning_of_month"]
        ).fillna(0).round(3) * 100

        if data["customer_churn_rate"].mean() < 1:
            data["customer_churn_rate"] = 0.833
        else:
            data = data.to_dict("records")
            data = json.dumps(data)
            return data

        data = data.round(4)
        data = data.to_dict("records")
        data = json.dumps(data)
        return data