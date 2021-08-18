import json
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin

from itertools import zip_longest

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
        ref_data = json.loads(result.text)
        data = ref_data
        
        dataset = data[0]['dataset']
        keys = data[0]['labels']
        product_dict = dict(zip_longest(keys, dataset))
     
        df_f = pd.DataFrame.from_dict(product_dict)

        df_f['Avg Investor Participation per Campaign'] = df_f['Investors Participated'] / df_f['No. of Campaigns']
        df_f['Avg Investor Investment Amount per Campaign'] = (df_f['Total Invested Amount'] / df_f['No. of Campaigns']) / (df_f['Investors Participated'] / df_f['No. of Campaigns'])
        data = df_f.round(1)

        data = data.to_dict('list')

        product_data = ref_data
        product_data[0]['dataset'][3] = data['Avg Investor Participation per Campaign']
        product_data[0]['dataset'][4] = data['Avg Investor Investment Amount per Campaign']
        data = product_data
        data = json.dumps(data)
        #print(data)
        return data