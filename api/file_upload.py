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
from openpyxl import Workbook, load_workbook
from requests.api import get
from requests.exceptions import HTTPError
from rich.console import Console
from werkzeug.utils import secure_filename

console = Console()

ALLOWED_EXCEL_EXTENSIONS = {"xlsx"}

from utils.default_data import default_portfolio

base_url = "https://blink.hackstrap.com/"

local_url = "http://127.0.0.1:5000/"

PREFIX = "Bearer"


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token


api_file_upload = Blueprint("api_file_upload", __name__)
CORS(api_file_upload)


@api_file_upload.route("/unity/v1/api/file_upload", methods=["POST"])
def file_upload():
    page = 0
    page_size = 12
    startup_id = request.args.get("startup_id")
    year = int
    month = int
    header = request.headers.get("Authorization")
    access_token = get_token(header)

    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            return "No file part"
        else:
            file = request.files["file"]
            if file.filename == "":
                return "No selected file"
            else:
                file = request.files["file"]
                filename = secure_filename(file.filename)
                file_extension = (
                    filename.rsplit(".", 1)[1].lower() in ALLOWED_EXCEL_EXTENSIONS
                )
                if file_extension == False:
                    return "Only xlsx file extension allowed"
                else:
                    file = request.files["file"]
                    # print(request.files)
                    print(startup_id)
                    filename = secure_filename(file.filename)
                    print(filename)

                    wb = load_workbook(request.files["file"])
                    print(wb.sheetnames)
                    sheet_list = [
                        "Info",
                        "Revenue",
                        "Users",
                        "Expense",
                        "Opex Expenses",
                        "Employee",
                        "Product",
                    ]

                    # check if sheetnames are in the sheet_list
                    for sheet in wb.sheetnames:
                        if sheet not in sheet_list:
                            return "Please upload the correct sheets"
                        else:

                            # ws = wb.active
                            # print(ws)
                            # print(ws.title)
                            # print(ws["A1"].value)

                            info_data = pd.read_excel(
                                request.files["file"],
                                sheet_name="Info",
                                dtype={"Format": str, "startup_id": str},
                            )
                            print(info_data)
                            print(info_data["Format"][0])
                            print(info_data["startup_id"][0])

                            revenue_data = pd.read_excel(
                                request.files["file"],
                                sheet_name="Revenue",
                                usecols=["Table Name", "Year"],
                                dtype={
                                    "Table Name": str,
                                },
                            )
                            revenue_data["Year"] = revenue_data["Year"].fillna(0)
                            revenue_data = revenue_data.astype({"Year": "int"})

                            year = revenue_data["Year"][0]
                            print(revenue_data)
                            print(revenue_data["Table Name"][0])
                            print(revenue_data["Year"][0])

                            revenue_data_table = pd.read_excel(
                                request.files["file"],
                                sheet_name="Revenue",
                                usecols=[
                                    "Table Column Name",
                                    "January",
                                    "February",
                                    "March",
                                    "April",
                                    "May",
                                    "June",
                                    "July",
                                    "August",
                                    "September",
                                    "October",
                                    "November",
                                    "December",
                                ],
                                dtype={
                                    "Table Name": str,
                                },
                            )

                            revenue_data_table = revenue_data_table.where(
                                revenue_data_table.notnull(), None
                            )

                            print(revenue_data_table)

                            revenue_data_table = revenue_data_table.set_index(
                                "Table Column Name"
                            )
                            revenue_data_table.index.names = [None]
                            revenue_data_table = revenue_data_table.transpose()

                            revenue_data_table = pd.DataFrame(
                                revenue_data_table, dtype=object
                            )
                            revenue_data_table.index = [
                                0,
                                1,
                                2,
                                3,
                                4,
                                5,
                                6,
                                7,
                                8,
                                9,
                                10,
                                11,
                            ]
                            print(revenue_data_table)

                            revenue_data_table["Total MRR"] = revenue_data_table[
                                "Total MRR"
                            ].astype(float)
                            revenue_data_table["Total New MRR"] = revenue_data_table[
                                "Total New MRR"
                            ].astype(float)
                            revenue_data_table[
                                "Total Non-Recurring Revenue"
                            ] = revenue_data_table[
                                "Total Non-Recurring Revenue"
                            ].astype(
                                float
                            )
                            revenue_data_table = revenue_data_table.where(
                                revenue_data_table.notnull(), None
                            )

                            # revenue_data_table_list = revenue_data_table[
                            #     "Total MRR"
                            # ].tolist()

                            print(revenue_data_table["Total MRR"][0])
                            print(type(revenue_data_table["Total MRR"][0]))
                            print(revenue_data_table["Total MRR"][6])
                            print(type(revenue_data_table["Total MRR"][6]))
                            print(revenue_data_table)

                            revenue_table_result = requests.get(
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

                            if len(revenue_table_result.text) < 4:

                                json_data = {
                                    "total_revenue": None,
                                    "total_revenue_gr": None,
                                    "total_mrr": 0,
                                    "total_mrr_gr": None,
                                    "total_new_mrr": 0,
                                    "total_non_recurring_revenue": 0,
                                    "gross_profit_margin": None,
                                    "startup_id": "",
                                    "last_updated": None,
                                    "month": 0,
                                    "year": 0,
                                }

                                total_mrr_list = revenue_data_table[
                                    "Total MRR"
                                ].tolist()

                                total_new_mrr_list = revenue_data_table[
                                    "Total New MRR"
                                ].tolist()

                                total_non_recurring_revenue_list = revenue_data_table[
                                    "Total Non-Recurring Revenue"
                                ].tolist()

                                range = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

                                for i in range:

                                    json_data["startup_id"] = str(startup_id)
                                    json_data["month"] = int(i + 1)
                                    json_data["year"] = int(year)
                                    json_data["total_mrr"] = total_mrr_list[i]
                                    json_data["total_new_mrr"] = total_new_mrr_list[i]
                                    json_data[
                                        "total_non_recurring_revenue"
                                    ] = total_non_recurring_revenue_list[i]

                                    print(json_data)

                                    r = requests.post(
                                        base_url + "v1/revenue/",
                                        data=json.dumps(json_data),
                                        headers={
                                            "Content-Type": "application/json",
                                            "Authorization": "Bearer {}".format(
                                                access_token
                                            ),
                                        },
                                    )

                                    # print(base_url + "v1/revenue/{}".format(id))
                                    # print(json_data)
                                    # print(r.text)

                                return "File Upload Success with Status Code:{}".format(
                                    r.status_code
                                )

                                # return "File Upload Success"

                            else:

                                revenue_table_result = json.loads(
                                    revenue_table_result.text
                                )
                                revenue_table_result = pd.DataFrame(
                                    revenue_table_result
                                )

                                try:
                                    revenue_table_result = (
                                        revenue_table_result.sort_values(
                                            by="month", ascending=True
                                        )
                                    )
                                except:
                                    # print("Block2")
                                    return jsonify([])

                                revenue_table_result = revenue_table_result.where(
                                    revenue_table_result.notnull(), None
                                )

                                print(revenue_table_result)
                                print(type(revenue_table_result["total_mrr"][0]))
                                print(type(revenue_table_result["total_mrr"][1]))

                                print(revenue_table_result["total_mrr"])
                                print(revenue_data_table["Total MRR"])

                                revenue_table_result["total_mrr"] = revenue_data_table[
                                    "Total MRR"
                                ]
                                revenue_table_result[
                                    "total_new_mrr"
                                ] = revenue_data_table["Total New MRR"]

                                revenue_table_result[
                                    "total_non_recurring_revenue"
                                ] = revenue_data_table["Total Non-Recurring Revenue"]

                                revenue_data = revenue_table_result

                                print(revenue_data)
                                print(type(revenue_data["total_mrr"][0]))
                                print(type(revenue_data["total_mrr"][1]))

                                revenue_data = revenue_data.to_dict(orient="records")

                                revenue_data = json.dumps(revenue_data)

                                range = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

                                for i in range:
                                    # print(revenue_table_result["_id"][i])
                                    # print(type(revenue_table_result["total_revenue"][i]))
                                    id_list = revenue_table_result["_id"].tolist()

                                    total_mrr_list = revenue_table_result[
                                        "total_mrr"
                                    ].tolist()

                                    total_new_mrr_list = revenue_table_result[
                                        "total_new_mrr"
                                    ].tolist()

                                    total_non_recurring_revenue_list = (
                                        revenue_table_result[
                                            "total_non_recurring_revenue"
                                        ].tolist()
                                    )

                                    json_data = {
                                        "total_mrr": 0,
                                        "total_new_mrr": 0,
                                        "total_non_recurring_revenue": 0,
                                    }

                                    json_data["total_mrr"] = total_mrr_list[i]
                                    json_data["total_new_mrr"] = total_new_mrr_list[i]
                                    json_data[
                                        "total_non_recurring_revenue"
                                    ] = total_non_recurring_revenue_list[i]

                                    id = id_list[i]
                                    # print(id)
                                    print(json_data)
                                    # print("v1/revenue/{}".format(id))

                                    r = requests.put(
                                        base_url + "v1/revenue/{}".format(id),
                                        data=json.dumps(json_data),
                                        headers={
                                            "Content-Type": "application/json",
                                            "Authorization": "Bearer {}".format(
                                                access_token
                                            ),
                                        },
                                    )

                                    # print(base_url + "v1/revenue/{}".format(id))
                                    # print(json_data)
                                    # print(r.text)

                                return "File Upload Success with Status Code:{}".format(
                                    r.status_code
                                )

                                # return "File Upload Success"
