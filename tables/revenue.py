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

from utils import helpers

base_url = "https://blink.hackstrap.com/"

PREFIX = "Bearer"


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token


tables_revenue = Blueprint("tables_revenue", __name__)
CORS(tables_revenue)

@tables_revenue.route("/unity/v1/revenue", methods=["GET"])
def revenue():
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
            + "v1/revenue?"
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
        + "v1/revenue?"
        + "page={}&page_size={}&startup_id={}&year={}".format(
            page, page_size, startup_id, year
        ),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )

    #----------------------------------------------------------------
    expense = requests.get(
       base_url
       + "v1/expense?"
       + "page={}&page_size={}&startup_id={}&year={}".format(
           page, page_size, startup_id, year
       ),
       headers={
           "Content-Type": "application/json",
           "Authorization": "Bearer {}".format(access_token),
       },
    )

    #--------------

    if result.text == "[]":
        return jsonify([])

    elif expense.text == "[]":
        data = json.loads(result.text)
        data = pd.DataFrame(data)

        data = data.sort_values(by="month")

        print(data)

        data["total_revenue"] = data["total_mrr"] + data["total_non_recurring_revenue"]
        
        data["total_revenue_gr"] = helpers.pct_change(data["total_revenue"])
        data["total_mrr_gr"] = helpers.pct_change(data["total_mrr"])
        

        data = data.replace([np.inf, -np.inf], np.nan)
        #data = data.fillna(0)
        data = data.round(4)
        data = data.where(data.notnull(), None)
        
        data = data.to_dict("records")
        data = json.dumps(data)
        return data


    else:
        data = json.loads(result.text)
        data = pd.DataFrame(data)

        data = data.sort_values(by="month")
        
        
        
        expense = json.loads(expense.text)
        expense = pd.DataFrame(expense)
        
        expense = expense.sort_values(by="month")
        
       
        
        data["total_revenue"] = data["total_mrr"] + data["total_non_recurring_revenue"]
       
        data["total_revenue_gr"] = helpers.pct_change(data["total_revenue"])
        data["total_mrr_gr"] = helpers.pct_change(data["total_mrr"])
       
        
        expense["total_customer_support_expenses"] = (
        expense["total_payroll_support"] + expense["software_and_tools_support"]
            )
        expense["total_service_delivery_expenses"] = expense["hosting_service_delivery"]
        expense["total_cost_of_goods_manufactured"] = (
            expense["direct_material_costs"]
            + expense["direct_labor_costs"]
            + expense["manufacturing_overhead"]
            + expense["net_wip_inventory"]
            )
        expense["total_cogs"] = (
            expense["total_cost_of_goods_manufactured"]
            + expense["net_finished_goods_inventory"]
            + expense["total_other_cogs"]
            )
        
        data["gross_profit_margin"] = (
            (data["total_revenue"] - expense["total_cogs"]) / data["total_revenue"]
        ) * 100
        
        #data = data.fillna(0)
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.round(4)
        data = data.where(data.notnull(), None)
        
        data = data.to_dict("records")
        data = json.dumps(data)
        return data