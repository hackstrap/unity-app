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


tables_product = Blueprint("tables_product", __name__)
CORS(tables_product)

@tables_product.route("/unity/v1/product", methods=["GET"])
def product():
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
            + "v1/product?"
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
        + "v1/product?"
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
    

        
     
        # data = data.round(4)
        # data = data.to_dict("records")
        # data = json.dumps(data)


        return result.text