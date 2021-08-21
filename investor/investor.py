import json
from datetime import datetime
import arrow as arw
import math

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

local_url = "http://127.0.0.1:5000/"

PREFIX = "Bearer"



default_portfolio = {'investor_id': '', 'investment_summary': [{'total_investment': None, 'current_total_investment_value': None, 'agg_net_irr_data': { }, 'startups_by': [{'filter': 'By Sector', 'data': [], 'labels': []}], 'aggregate_multiple': None, 'total_startups': 0, 'organization': 'Tyke'}], 'startup_summary': [{'startup_id': '', 'total_money_invested': 0.0, 'current_investment_value': 0.0, 'multiple': 0.0, 'startup_net_irr_data': {'2020': [0.0, 0.0, 0.0, 0.0]}, 'investment_time': {'in_months': [0, 0], 'in_days': 0, 'in_years': 0.0}, 'organization': [{'fees': 0.0, 'carry': 0.0, 'one_time_fees': 0.0, 'name': 'Tyke', 'discount': 0.0, 'valuation_cap': 0.0, 'entry_valuation': 0.0}]}]}



def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != PREFIX:
        raise ValueError("Invalid token")

    return token

investor_investment_summary = Blueprint("investor_investment_summary", __name__)
CORS(investor_investment_summary)

@investor_investment_summary.route("/unity/v1/investor/investment_summary", methods=["GET"])
def investment_summary():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    header = request.headers.get("Authorization")
    access_token = get_token(header)
    now_year_India = arw.now('Asia/Kolkata').year


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
        + "page={}&page_size={}&investor_id={}".format(page, page_size, investor_id),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )

        investor_startups_by_sectors_result = requests.get(
        base_url
        + "/unity/v1/investor/investor_startups_by_sectors?"
        + "page={}&page_size={}&investor_id={}".format(page, page_size, investor_id),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        },
    )   

        
        
        


        if investment_total_result.status_code == 200:
            investment_total_result = investment_total_result.json()

            if startups_invested_result.status_code == 200:
                startups_invested_result = startups_invested_result.json()
                #print(len(startups_invested_result["{}".format(investor_id)]))
                #print(type(startups_invested_result["{}".format(investor_id)]))

                if investor_startups_by_sectors_result.status_code == 200:
                    investor_startups_by_sectors_result = investor_startups_by_sectors_result.json()
                    #print(investor_startups_by_sectors_result[0])
                    #print(investor_startups_by_sectors_result[1])

                    data = default_portfolio      
                    data = data["investment_summary"][0]
                    data["total_investment"] = investment_total_result["amount"]["{}".format(investor_id)]
                    data["total_startups"] = len(startups_invested_result["{}".format(investor_id)])

                    #print(data["startups_by"][0]["labels"])

                    data["startups_by"][0]["data"] = investor_startups_by_sectors_result[1]
                    data["startups_by"][0]["labels"] = investor_startups_by_sectors_result[0]
                    
                    #calculate investor_agg_irr)
                    year_instance = arw.now('Asia/Kolkata')
                    no_of_quaters = math.ceil(year_instance.month/3.)
                    investor_agg_irr = ([None] * no_of_quaters)
      
                    data["agg_net_irr_data"]["{}".format(now_year_India)] = investor_agg_irr
            
                    return data


                #When investor_startups_by_sectors_result is not 200     
                else:

                    data = default_portfolio      
                    data = data["investment_summary"][0]
                    data["total_investment"] = investment_total_result["amount"]["{}".format(investor_id)]
                    data["total_startups"] = len(startups_invested_result["{}".format(investor_id)])
                    
                    #calculate investor_agg_irr)
                    year_instance = arw.now('Asia/Kolkata')
                    no_of_quaters = math.ceil(year_instance.month/3.)
                    investor_agg_irr = ([None] * no_of_quaters)
      
                    data["agg_net_irr_data"]["{}".format(now_year_India)] = investor_agg_irr
                              
                    return data

            
            #When investment_total_result is not 200    
            else:
                data = default_portfolio      
                data = data["investment_summary"][0]
                data["total_investment"] = investment_total_result["amount"]["{}".format(investor_id)]
                
                #calculate investor_agg_irr)
                year_instance = arw.now('Asia/Kolkata')
                no_of_quaters = math.ceil(year_instance.month/3.)
                investor_agg_irr = ([None] * no_of_quaters)
      
                data["agg_net_irr_data"]["{}".format(now_year_India)] = investor_agg_irr
                 
                return data
           
        #When investment_total_result is not 200    
        else:
            data = default_portfolio      
            data = data["investment_summary"][0]
            
            #calculate investor_agg_irr)
            year_instance = arw.now('Asia/Kolkata')
            no_of_quaters = math.ceil(year_instance.month/3.)
            investor_agg_irr = ([None] * no_of_quaters)
      
            data["agg_net_irr_data"]["{}".format(now_year_India)] = investor_agg_irr
            
            return data


investor_startup_summary = Blueprint("investor_startup_summary", __name__)

@investor_startup_summary.route("/unity/v1/investor/startup_summary", methods=["GET"])
def startup_summary():
    page = request.args.get("page")
    page_size = request.args.get("page_size")
    investor_id = request.args.get("investor_id")
    header = request.headers.get("Authorization")
    access_token = get_token(header)


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
        data = default_portfolio 
        data = data["startup_summary"][0]
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
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)

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
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)

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
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.where(data.notnull(), None)
        data = data.groupby(by=["investor_id", "year", "month"])["amount"].sum()
        data = data.reset_index().to_json(orient="records")
        return data



investor_investor_startups_by_sectors = Blueprint("investor_investor_startups_by_sectors", __name__)

@investor_investor_startups_by_sectors.route("/unity/v1/investor/investor_startups_by_sectors", methods=["GET"])
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
        startups = startups[["startup_name" , "startup_id" , "sectors"]]
        

        startups_total = pd.merge(startups, investment_data, on="startup_id")
        # print(startups_total)

        startups_array = startups_total[["startup_id" , "sectors"]]
        # print(startups_array)

        


        #startups_array = startups_array.groupby(by=["startup_id"])
        startups_array = startups_array.groupby(by=["startup_id"])["sectors"].unique()
        #startups_array.apply(print)
        #print(startups_array)
        #print(startups_array.reset_index(name='sectors'))

        sectors_df = pd.DataFrame(startups_array.reset_index(name='sectors'))
        #print(type(sectors_df["sectors"].iloc[0]))
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
        #print(sectors_df['sectors'].value_counts())

        df = sectors_df['sectors'].value_counts().rename_axis('sectors').reset_index(name='counts')
      
        df["counts"] = (100. * df["counts"] / df["counts"].sum()).round(0)

        #print(df)

        list_of_sectors = df['sectors'].tolist()
        list_of_counts = df['counts'].tolist()
     

        #return list of sectors and list of counts as json    
        return jsonify(list_of_sectors, list_of_counts)  

         
       

       
