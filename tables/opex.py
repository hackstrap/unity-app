import json
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin

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


tables_opex = Blueprint("tables_opex", __name__)
CORS(tables_opex)

@tables_opex.route("/unity/v1/opex", methods=["GET"])
def opex():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    startup_id = request.args.get("startup_id")
    year = request.args.get("year")
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    result = requests.get(
        base_url
        + "v1/opex?"
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
        data = data.fillna(value=np.nan)
        try:
            data = data.sort_values(by="month", ascending=True)
        except:
            return jsonify([])
        
        data["total_opex_expenses"] = (
            data["total_general_and_administrative_expenses"]
            + data["total_sales_and_marketing_expenses"]
            + data["total_research_and_development_expenses"]
        )

        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.round(4)
        data = data.where(data.notnull(), None)
        
        data = data.to_dict("records")
        data = json.dumps(data)
        return data