import datetime
import json
import math
from datetime import date, datetime

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


api_quickbooks_upload = Blueprint("api_quickbooks_upload", __name__)
CORS(api_quickbooks_upload)


@api_quickbooks_upload.route("/unity/v1/api/quickbooks_upload", methods=["POST"])
def quickbooks_upload():
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

                    # return "File uploaded successfully"

                    if filename == "Balance_sheet.xlsx":

                        balance_sheet_df = pd.read_excel(file)
                        # print(balance_sheet_df)

                        balance_sheet_df = balance_sheet_df.where(
                            balance_sheet_df.notnull(), None
                        )

                        balance_sheet_json = balance_sheet_df.to_json()
                        balance_sheet_dict = json.loads(balance_sheet_json)

                        # check for balance sheet record

                        # If all data is True

                        all_data = "true"

                        balance_sheet_data_record_result = requests.get(
                            base_url
                            + "v1/quickbooks?"
                            + "page={}&page_size={}&startup_id={}&sheet_name={}&all_data={}".format(
                                page,
                                page_size,
                                startup_id,
                                filename,
                                all_data,
                            ),
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": "Bearer {}".format(access_token),
                            },
                        )

                        # If all data does not exist

                        if len(balance_sheet_data_record_result.text) < 4:

                            print(balance_sheet_data_record_result.text)

                            balance_sheet_data_record = {
                                "startup_id": "",
                                "sheet_name": "",
                                "balance_sheet_data": {},
                                "all_data": None,
                                "year": None,
                                "month": None,
                            }

                            balance_sheet_data_record["startup_id"] = str(startup_id)
                            balance_sheet_data_record["sheet_name"] = str(filename)
                            balance_sheet_data_record["all_data"] = str(all_data)

                            balance_sheet_data_record["year"] = datetime.now().year
                            balance_sheet_data_record["month"] = datetime.now().month

                            balance_sheet_data_record[
                                "balance_sheet_data"
                            ] = balance_sheet_dict

                            r = requests.post(
                                base_url + "v1/quickbooks/",
                                data=json.dumps(balance_sheet_data_record),
                                headers={
                                    "Content-Type": "application/json",
                                    "Authorization": "Bearer {}".format(access_token),
                                },
                            )

                            # print(r.text)
                            return "Balance_sheet processed with code '{}'".format(
                                r.text
                            )

                            # print(balance_sheet_data_record)

                        # If all data exist
                        else:

                            balance_sheet_data_record = {
                                "balance_sheet_data": {},
                                "year": None,
                                "month": None,
                            }

                            # print(balance_sheet_data_record["balance_sheet_data"])

                            balance_sheet_data_record[
                                "balance_sheet_data"
                            ] = balance_sheet_dict
                            balance_sheet_data_record["year"] = datetime.now().year
                            balance_sheet_data_record["month"] = datetime.now().month

                            id = balance_sheet_data_record_result.json()[0]["_id"]

                            r = requests.put(
                                base_url + "v1/quickbooks/{}".format(id),
                                data=json.dumps(balance_sheet_data_record),
                                headers={
                                    "Content-Type": "application/json",
                                    "Authorization": "Bearer {}".format(access_token),
                                },
                            )

                            # print(r.text)
                            return "Balance_sheet processed with code '{}'".format(
                                r.text
                            )

                            # print(balance_sheet_data_record_result.text)

                        # return "Balance_sheet updated with code {}".format(r.text)

                    elif filename == "Customers.xlsx":

                        customers_sheet_df = pd.read_excel(
                            file,
                            # sheet_name="Customer Contact List",
                            header=4,
                            usecols=[
                                "Customer",
                                "Phone Numbers",
                                "Email",
                                "Full Name",
                                "Billing Address",
                                "Shipping Address",
                            ],
                        )
                        print(customers_sheet_df)

                        return "Customers.xlsx uploaded successfully"

                    elif filename == "Employees.xlsx":

                        employees_sheet_df = pd.read_excel(
                            file,
                            # sheet_name="Employee Contact List",
                            header=4,
                            usecols=[
                                "Employee",
                                "Phone Numbers",
                                "Email",
                                "Address",
                            ],
                        )
                        print(employees_sheet_df)

                        return "Employees.xlsx uploaded successfully"

                    elif filename == "General_ledger.xlsx":
                        return "General_ledger.xlsx uploaded successfully"

                    elif filename == "Journal.xlsx":
                        return "Journal.xlsx uploaded successfully"

                    elif filename == "Profit_and_loss.xlsx":
                        return "Profit_and_loss.xlsx uploaded successfully"

                    elif filename == "Suppliers.xlsx":

                        supplier_sheet_df = pd.read_excel(
                            file,
                            # sheet_name="Supplier Contact List",
                            header=4,
                            usecols=[
                                "Supplier",
                                "Phone Numbers",
                                "Full Name",
                                "Address",
                                "Account No.",
                            ],
                        )
                        print(supplier_sheet_df)

                        return "Suppliers.xlsx uploaded successfully"

                    elif filename == "Trial_balance.xlsx":
                        return "Trial_balance.xlsx uploaded successfully"

                    else:
                        return "Invalid file uploaded"
