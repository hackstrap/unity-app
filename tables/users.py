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


tables_users = Blueprint("tables_users", __name__)
CORS(tables_users)

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
    users = requests.get(
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

    revenue = requests.get(
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

    opex = requests.get(
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

    if users.text == "[]":
        return jsonify([])

    elif revenue.text == "[]" or opex.text == "[]":
        users = json.loads(users.text)
        users = pd.DataFrame(users)
        users = users.sort_values(by="month")


        users["total_customers"] = (
        users["total_customers_at_beginning_of_month"]
        + users["total_new_customers_acquired"]
        - users["total_customers_churned"]
    )
        users["total_monthly_active_users_gr"] = (
        users["total_monthly_active_users"].pct_change().fillna(0) * 100
    )
        users["customer_churn_rate"] = (
        users["total_customers_churned"] / users["total_customers_at_beginning_of_month"]
        ).fillna(0) * 100

        if users["customer_churn_rate"].mean() < 1:
            users["customer_churn_rate"] = 0.833
            users = users.replace([np.inf, -np.inf], np.nan)
            users = users.where(users.notnull(), None)
        else:
            users = users.replace([np.inf, -np.inf], np.nan)
            users = users.round(4)
            users = users.where(users.notnull(), None)
            users = users.to_dict("records")
            users = json.dumps(users)
            return users

        users = users.replace([np.inf, -np.inf], np.nan)
        users = users.round(4)
        users = users.where(users.notnull(), None)
        
        users = users.to_dict("records")
        users = json.dumps(users)
        return users

    elif revenue.text == "[]":
        users = json.loads(users.text)
        users = pd.DataFrame(users)
        users = users.sort_values(by="month")

        opex = json.loads(opex.text)
        opex = pd.DataFrame(opex)    
        opex = opex.sort_values(by="month")



        users["total_customers"] = (
        users["total_customers_at_beginning_of_month"]
        + users["total_new_customers_acquired"]
        - users["total_customers_churned"]
    )
        users["total_monthly_active_users_gr"] = (
        users["total_monthly_active_users"].pct_change().fillna(0) * 100
    )
        users["customer_churn_rate"] = (
        users["total_customers_churned"] / users["total_customers_at_beginning_of_month"]
        ).fillna(0) * 100
        users = users.replace([np.inf, -np.inf], np.nan)
        users = users.round(4)


        if users["customer_churn_rate"].mean() < 1:
            users["customer_churn_rate"] = 0.833
        else:
            users["customer_acquisition_cost"] = (
                opex["total_sales_and_marketing_expenses"]
                / users["total_new_customers_acquired"]
            ).fillna(0)
            
            if users["customer_acquisition_cost"].mean() < 1:
                users["customer_acquisition_cost"] = 1

            else:
                users = users.round(4)
                users = users.where(users.notnull(), None)
                
                users = users.to_dict("records")
                users = json.dumps(users)
                return users

            users = users.round(4)
            users = users.where(users.notnull(), None)
            
            users = users.to_dict("records")
            users = json.dumps(users)
            return users

        users = users.round(4)
        users = users.where(users.notnull(), None)
        
        users = users.to_dict("records")
        users = json.dumps(users)
        return users


    else:
        users = json.loads(users.text)
        users = pd.DataFrame(users)
        users = users.fillna(0)
        users = users.sort_values(by="month")

        revenue = json.loads(revenue.text)
        revenue = pd.DataFrame(revenue)
        revenue = revenue.fillna(0)
        revenue = revenue.sort_values(by="month")

        opex = json.loads(opex.text)
        opex = pd.DataFrame(opex)
        opex = opex.fillna(0)
        opex = opex.sort_values(by="month")



        users["total_customers"] = (
        users["total_customers_at_beginning_of_month"]
        + users["total_new_customers_acquired"]
        - users["total_customers_churned"]
    )
        users["total_monthly_active_users_gr"] = (
        users["total_monthly_active_users"].pct_change().fillna(0) * 100
    )
        users["customer_churn_rate"] = (
        users["total_customers_churned"] / users["total_customers_at_beginning_of_month"]
        ).fillna(0) * 100
        
        users = users.replace([np.inf, -np.inf], np.nan)
        users = users.round(4)
        users = users.where(users.notnull(), None)

        if users["customer_churn_rate"].mean() < 1:
            users["customer_churn_rate"] = 0.833
        else:
            users["customer_acquisition_cost"] = (
                opex["total_sales_and_marketing_expenses"]
                / users["total_new_customers_acquired"]
            ).fillna(0).round(3)

            if users["customer_acquisition_cost"].mean() < 1:
                users["customer_acquisition_cost"] = 1

            else:
                users["customer_lifetime_value"] = (
                    (revenue["total_mrr"] + revenue["total_non_recurring_revenue"])
                    / (
                        (
                            users["total_customers_at_beginning_of_month"]
                            + users["total_new_customers_acquired"]
                            - users["total_customers_churned"]
                        ).fillna(0)
                        * (
                            (
                                users["total_customers_churned"]
                                / users["total_customers_at_beginning_of_month"]
                            ).fillna(0)
                        ).fillna(0)
                        * 100
                    ).fillna(0)
                )
                users["ltv_to_cac_ratio"] = (
                    users["customer_lifetime_value"] / users["customer_acquisition_cost"]
                ).fillna(0)
                users = users.replace([np.inf, -np.inf], np.nan)
                users = users.round(4)
                users = users.where(users.notnull(), None)
                users = users.to_json(orient="records")
                return users

            users["customer_lifetime_value"] = (
                (revenue["total_mrr"] + revenue["total_non_recurring_revenue"])
                / (
                    (
                        users["total_customers_at_beginning_of_month"]
                        + users["total_new_customers_acquired"]
                        - users["total_customers_churned"]
                    ).fillna(0)
                    * (
                        (
                            users["total_customers_churned"]
                            / users["total_customers_at_beginning_of_month"]
                        ).fillna(0)
                    ).fillna(0)
                    * 100
                ).fillna(0)
            )
            users["ltv_to_cac_ratio"] = (
                users["customer_lifetime_value"] / users["customer_acquisition_cost"]
            ).fillna(0)
            users = users.replace([np.inf, -np.inf], np.nan)
            users = users.round(4)
            users = users.where(users.notnull(), None)
            users = users.to_json(orient="records")
            return users

        users["customer_acquisition_cost"] = (
            opex["total_sales_and_marketing_expenses"]
            / users["total_new_customers_acquired"]
        ).fillna(0)
        users["customer_lifetime_value"] = (
            (revenue["total_mrr"] + revenue["total_non_recurring_revenue"])
            / (
                (
                    users["total_customers_at_beginning_of_month"]
                    + users["total_new_customers_acquired"]
                    - users["total_customers_churned"]
                ).fillna(0)
                * (
                    (
                        users["total_customers_churned"]
                        / users["total_customers_at_beginning_of_month"]
                    ).fillna(0)
                ).fillna(0)
                * 100
            ).fillna(0)
        )
        users["ltv_to_cac_ratio"] = (
            users["customer_lifetime_value"] / users["customer_acquisition_cost"]
        ).fillna(0)

        users = users.replace([np.inf, -np.inf], np.nan)
        users = users.round(4)
        users = users.where(users.notnull(), None)

        
        users = users.to_json(orient="records")
        return users

