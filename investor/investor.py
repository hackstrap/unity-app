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


investor_investment_summary = Blueprint("investor_investment_summary", __name__)
CORS(investor_investment_summary)


@investor_investment_summary.route(
    "/unity/v1/investor/investment_summary", methods=["GET"]
)
def investment_summary():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    header = request.headers.get("Authorization")
    access_token = get_token(header)
    now_year_India = arw.now("Asia/Kolkata").year
    now_month_India = arw.now("Asia/Kolkata").month

    startups_invested_result = requests.get(
        base_url
        + "/unity/v1/investor/startups_invested?"
        + "page={}&page_size={}&investor_id={}".format(page, page_size, investor_id),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )

    if startups_invested_result.json() == []:
        return jsonify([])

    else:

        investment_total_result = requests.get(
            base_url
            + "/unity/v1/investor/investment_total?"
            + "page={}&page_size={}&investor_id={}".format(
                page, page_size, investor_id
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

        investor_startups_by_sectors_result = requests.get(
            base_url
            + "/unity/v1/investor/investor_startups_by_sectors?"
            + "page={}&page_size={}&investor_id={}".format(
                page, page_size, investor_id
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

        investments_result = requests.get(
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

        if investment_total_result.status_code == 200:
            investment_total_result = investment_total_result.json()

            if startups_invested_result.status_code == 200:
                startups_invested_result = startups_invested_result.json()
                # print(len(startups_invested_result["{}".format(investor_id)]))
                # print(type(startups_invested_result["{}".format(investor_id)]))

                if investor_startups_by_sectors_result.status_code == 200:
                    investor_startups_by_sectors_result = (
                        investor_startups_by_sectors_result.json()
                    )
                    # print(investor_startups_by_sectors_result[0])
                    # print(investor_startups_by_sectors_result[1])

                    if investments_result.status_code == 200:
                        investments_result = investments_result.text
                        investments_result = json.loads(investments_result)
                        investments_result = pd.DataFrame(investments_result)

                        # Get datetime from mongoDB and convert it to local time
                        try:
                            investments_result["date"] = investments_result[
                                "date"
                            ].apply(parser.parse)
                        except:
                            return jsonify([])
                        # print(investments_result)

                        investments_result["date"] = investments_result[
                            "date"
                        ].dt.tz_convert(None)

                        # print(investments_result)

                        investments_result["date"] = investments_result[
                            "date"
                        ].dt.tz_localize("Asia/Kolkata")

                        # print((investments_result["date"].iloc[0]))

                        investments_data = investments_result

                        try:
                            all_transactions = investments_data.shape[0]
                        except:
                            all_transactions = None
                        # print(type(all_transactions))

                        # print(investments_data)

                        investments_data_this_year = investments_data[
                            investments_data["date"].dt.year == now_year_India
                        ]

                        try:
                            this_year = investments_data_this_year.shape[0]
                        except:
                            this_year = None
                        # print(type(this_year))

                        try:
                            last_three_months_data = investments_data_this_year[
                                investments_data_this_year["date"].dt.month.isin(
                                    [
                                        now_month_India - 1,
                                        now_month_India - 2,
                                        now_month_India - 3,
                                    ]
                                )
                            ]
                            last_three_months = last_three_months_data.shape[0]
                        except:
                            last_three_months = None
                        # print(type(last_three_months))

                        data = default_portfolio
                        data = data["investment_summary"][0]
                        data["total_investment"] = investment_total_result["amount"][
                            "{}".format(investor_id)
                        ]
                        data["total_startups"] = len(
                            startups_invested_result["{}".format(investor_id)]
                        )

                        # print(data["startups_by"][0]["labels"])

                        data["startups_by"][0][
                            "data"
                        ] = investor_startups_by_sectors_result[1]
                        data["startups_by"][0][
                            "labels"
                        ] = investor_startups_by_sectors_result[0]

                        # calculate investor_agg_irr)
                        year_instance = arw.now("Asia/Kolkata")
                        no_of_quaters = math.ceil(year_instance.month / 3.0)
                        investor_agg_irr = [None] * no_of_quaters

                        data["agg_net_irr_data"][
                            "{}".format(now_year_India)
                        ] = investor_agg_irr

                        data["total_transactions"][
                            "all_transactions"
                        ] = all_transactions
                        data["total_transactions"][
                            "last_three_months"
                        ] = last_three_months
                        data["total_transactions"]["this_year"] = this_year

                        return data

                    # When investments_result is not 200
                    else:

                        data = default_portfolio
                        data = data["investment_summary"][0]
                        data["total_investment"] = investment_total_result["amount"][
                            "{}".format(investor_id)
                        ]
                        data["total_startups"] = len(
                            startups_invested_result["{}".format(investor_id)]
                        )

                        # print(data["startups_by"][0]["labels"])

                        data["startups_by"][0][
                            "data"
                        ] = investor_startups_by_sectors_result[1]
                        data["startups_by"][0][
                            "labels"
                        ] = investor_startups_by_sectors_result[0]

                        # calculate investor_agg_irr)
                        year_instance = arw.now("Asia/Kolkata")
                        no_of_quaters = math.ceil(year_instance.month / 3.0)
                        investor_agg_irr = [None] * no_of_quaters

                        data["agg_net_irr_data"][
                            "{}".format(now_year_India)
                        ] = investor_agg_irr

                        return data

                # When investor_startups_by_sectors_result is not 200
                else:

                    data = default_portfolio
                    data = data["investment_summary"][0]
                    data["total_investment"] = investment_total_result["amount"][
                        "{}".format(investor_id)
                    ]
                    data["total_startups"] = len(
                        startups_invested_result["{}".format(investor_id)]
                    )

                    # calculate investor_agg_irr)
                    year_instance = arw.now("Asia/Kolkata")
                    no_of_quaters = math.ceil(year_instance.month / 3.0)
                    investor_agg_irr = [None] * no_of_quaters

                    data["agg_net_irr_data"][
                        "{}".format(now_year_India)
                    ] = investor_agg_irr

                    return data

            # When investment_total_result is not 200
            else:
                data = default_portfolio
                data = data["investment_summary"][0]
                data["total_investment"] = investment_total_result["amount"][
                    "{}".format(investor_id)
                ]

                # calculate investor_agg_irr)
                year_instance = arw.now("Asia/Kolkata")
                no_of_quaters = math.ceil(year_instance.month / 3.0)
                investor_agg_irr = [None] * no_of_quaters

                data["agg_net_irr_data"]["{}".format(now_year_India)] = investor_agg_irr

                return data

        # When investment_total_result is not 200
        else:
            data = default_portfolio
            data = data["investment_summary"][0]

            # calculate investor_agg_irr)
            year_instance = arw.now("Asia/Kolkata")
            no_of_quaters = math.ceil(year_instance.month / 3.0)
            investor_agg_irr = [None] * no_of_quaters

            data["agg_net_irr_data"]["{}".format(now_year_India)] = investor_agg_irr

            return data


investor_startup_summary = Blueprint("investor_startup_summary", __name__)


@investor_startup_summary.route("/unity/v1/investor/startup_summary", methods=["GET"])
def startup_summary():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    startup_id = request.args.get("startup_id")
    header = request.headers.get("Authorization")
    access_token = get_token(header)
    now_year_India = arw.now("Asia/Kolkata").year

    if startup_id == None or startup_id == " " or startup_id == []:

        startups_invested_result = requests.get(
            base_url
            + "/unity/v1/investor/startups_invested?"
            + "page={}&page_size={}&investor_id={}".format(
                page, page_size, investor_id
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

        if startups_invested_result.json() == []:
            return jsonify([])

        else:
            data = default_portfolio
            data = data["startup_summary"][0]
            return data

    else:

        startup_investment_total_result = requests.get(
            base_url
            + "/unity/v1/investor/startup_investment_total?"
            + "page={}&page_size={}&investor_id={}&startup_id={}".format(
                page, page_size, investor_id, startup_id
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )

        startups_invested_result = requests.get(
            base_url
            + "/unity/v1/investor/startups_invested?"
            + "page={}&page_size={}&investor_id={}".format(
                page, page_size, investor_id
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access_token),
            },
        )
        # print(startups_invested_result.json())
        # print(startup_investment_total_result.text)

        if startup_investment_total_result == None:
            return jsonify([])

        else:

            startups_invested_data = startups_invested_result.json()
            # print(startups_invested_data)
            startup_investment_total_data = startup_investment_total_result.json()

            data = default_portfolio
            data = data["startup_summary"][0]
            data["investment_time"] = startup_investment_total_data["investment_time"]
            data["startup_id"] = startup_investment_total_data["startup_id"]
            data["total_money_invested"] = startup_investment_total_data[
                "total_money_invested"
            ]

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
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)

        data = pd.DataFrame(data.groupby(by=["investor_id"])["amount"].sum())
        data = data.to_dict()
        data = json.dumps(data)
        return data


investor_startups_invested = Blueprint("investor_startups_invested", __name__)


@investor_startups_invested.route(
    "/unity/v1/investor/startups_invested", methods=["GET"]
)
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
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)

        data = data.groupby(by=["investor_id"])["startup_id"].unique()
        data = data.to_json(orient="index")
        return data


investor_investor_startups = Blueprint("investor_investor_startups", __name__)


@investor_investor_startups.route(
    "/unity/v1/investor/investor_startups", methods=["GET"]
)
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

        startups_array = startups_array.groupby(by=["investor_id"])[
            "startup_id"
        ].unique()

        data = pd.DataFrame(
            startups_array["{}".format(investor_id)], columns=["startup_id"]
        )
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)

        data = pd.merge(data, startups, on="startup_id")
        data = data.to_json(orient="index")

        return data


investor_investments_month = Blueprint("investor_investments_month", __name__)


@investor_investments_month.route(
    "/unity/v1/investor/investments_month", methods=["GET"]
)
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
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)
        data = data.groupby(by=["investor_id", "year", "month"])["amount"].sum()
        data = data.reset_index().to_json(orient="records")
        return data


investor_investor_startups_by_sectors = Blueprint(
    "investor_investor_startups_by_sectors", __name__
)


@investor_investor_startups_by_sectors.route(
    "/unity/v1/investor/investor_startups_by_sectors", methods=["GET"]
)
def investor_startups_by_sectors():
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
        investment_data = json.loads(result.text)
        investment_data = pd.DataFrame(investment_data)

        startups = json.loads(startups.text)
        startups = pd.DataFrame(startups)
        startups = startups[["startup_name", "startup_id", "sectors"]]

        startups_total = pd.merge(startups, investment_data, on="startup_id")
        # print(startups_total)

        startups_array = startups_total[["startup_id", "sectors"]]
        # print(startups_array)

        # startups_array = startups_array.groupby(by=["startup_id"])
        startups_array = startups_array.groupby(by=["startup_id"])["sectors"].unique()
        # startups_array.apply(print)
        # print(startups_array)
        # print(startups_array.reset_index(name='sectors'))

        sectors_df = pd.DataFrame(startups_array.reset_index(name="sectors"))
        # print(type(sectors_df["sectors"].iloc[0]))
        x = sectors_df["sectors"].to_numpy()

        z = []
        for i in x:
            i = i[0]
            z.append(i)
        # print(z)

        # print(x)
        # print(type(x))

        sectors_df["sectors"] = pd.DataFrame(z)

        # print(sectors_df)
        # print(type(sectors_df))
        # print(sectors_df['sectors'].value_counts())

        df = (
            sectors_df["sectors"]
            .value_counts()
            .rename_axis("sectors")
            .reset_index(name="counts")
        )

        df["counts"] = (100.0 * df["counts"] / df["counts"].sum()).round(0)

        # print(df)

        list_of_sectors = df["sectors"].tolist()
        list_of_counts = df["counts"].tolist()

        # return list of sectors and list of counts as json
        return jsonify(list_of_sectors, list_of_counts)


investor_startup_investment_total = Blueprint(
    "investor_startup_investment_total", __name__
)


@investor_startup_investment_total.route(
    "/unity/v1/investor/startup_investment_total", methods=["GET"]
)
def startup_investment_total():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    startup_id = request.args.get("startup_id")
    year = request.args.get("year")
    header = request.headers.get("Authorization")
    access_token = get_token(header)
    now_year_India = arw.now("Asia/Kolkata").year
    now_India = arw.now("Asia/Kolkata")
    tz_India_info = "Asia/Kolkata"

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

    # print(result.text)

    if result.text == "[]":
        return jsonify([])

    else:
        data = json.loads(result.text)
        data = pd.DataFrame(data)
        # data = data.replace([np.inf, -np.inf], np.nan)
        # data = data.where(data.notnull(), None)

        data_startup_invested = data[["startup_id", "campaign_id", "date", "amount"]]

        try:
            data_startup_invested = data_startup_invested.loc[
                data_startup_invested["startup_id"] == "{}".format(startup_id)
            ]
        except:
            return jsonify([])

        try:
            data_startup_invested = data_startup_invested.sort_values(
                by="date", ascending=True
            )
        except:
            return jsonify([])

        # print(data_startup_invested)

        # Number of transactions made in the startup (shape[0] is the number of transactions)
        startup_total_number_of_transactions = data_startup_invested.shape[0]
        # print(startup_total_number_of_transactions)

        # Total amount invested in the startup
        startup_total_amount = data_startup_invested.groupby(by=["startup_id"])[
            "amount"
        ].sum()

        try:
            total_money_invested = startup_total_amount[0]
        except:
            return jsonify([])

        # print(total_money_invested)

        # date first invested in a startup
        # first_date = data_startup_invested['date'].min()
        # print(first_date)

        # sort data by date
        try:
            data_startup_invested = data_startup_invested.sort_values(
                by="date", ascending=True
            )
        except:
            return jsonify([])

        # print(data_startup_invested)

        data_startup_invested["date"] = data_startup_invested["date"].apply(
            parser.parse
        )

        data_startup_invested["date"] = data_startup_invested["date"].dt.tz_convert(
            None
        )

        print(data_startup_invested)

        data_startup_invested["date"] = data_startup_invested["date"].dt.tz_localize(
            "Asia/Kolkata"
        )

        print(data_startup_invested)

        try:
            first_date_of_transaction = data_startup_invested["date"].iloc[0]
        except:
            return jsonify([])

        # Converting pandas.tslib.Timestamp to datetime python object

        # first_date_of_transaction = first_date_of_transaction.to_pydatetime()

        # print(data_startup_invested)
        # print(first_date_of_transaction)

        # add time zone to date string to get datetime object
        # first_date_of_transaction = first_date_of_transaction + tz.tzoffset('IST', 19800)

        # print((first_date_of_transaction))

        first_date_of_transaction_with_timezone = first_date_of_transaction.astimezone(
            pytz.timezone("Asia/Calcutta")
        )

        # print(type(first_date_of_transaction_with_timezone))
        print((first_date_of_transaction_with_timezone))
        # data_startup_invested_parsed

        now_India_dt = now_India.astimezone(pytz.timezone("Asia/Calcutta"))
        #print(type(now_India))
        #print(type(now_India_dt))

        # calculate investment time in years and months since date of first transaction made in the startup
        investment_time_diff = relativedelta(
            now_India_dt, first_date_of_transaction_with_timezone
        )
        investment_time_in_years_months_days = [
            investment_time_diff.years,
            investment_time_diff.months,
            investment_time_diff.days,
        ]
        # print(investment_time_in_years_months_days)

        investment_time_in_days_diff = (
            now_India_dt - first_date_of_transaction_with_timezone
        )
        investment_time_in_days = investment_time_in_days_diff.days
        # print((investment_time_in_days))

        startup_summary_data = {
            "startup_id": "{}".format(startup_id),
            "total_money_invested": 0.0,
            "investment_time": {
                "in_year_month_day": [],
                "in_days": 0,
                "startup_total_number_of_transactions": 0,
            },
        }

        # print(type(investment_time_in_days))

        startup_summary_data["total_money_invested"] = float(total_money_invested)
        startup_summary_data["investment_time"][
            "in_year_month_day"
        ] = investment_time_in_years_months_days
        startup_summary_data["investment_time"]["in_days"] = investment_time_in_days
        startup_summary_data["investment_time"][
            "startup_total_number_of_transactions"
        ] = int(startup_total_number_of_transactions)

        data = startup_summary_data
        return data
    


investor_startup_investors = Blueprint("investor_startup_investors", __name__)


@investor_startup_investors.route(
    "/unity/v1/investor/startup_investors", methods=["GET"]
)
def startup_investors():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    #investor_id = request.args.get("investor_id")
    startup_id = request.args.get("startup_id")
    year = request.args.get("year")
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    result = requests.get(
        base_url
        + "v1/investment?"
        + "page={}&page_size={}&startup_id={}".format(page, page_size, startup_id),
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
        
        data = data["investor_id"].unique()
        data = data.tolist()
        data = json.dumps(data)
       
        return data