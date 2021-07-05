from flask import Flask, jsonify, request
from datetime import datetime
import requests
from requests.exceptions import HTTPError
import json
import numpy as np
import pandas as pd
from requests.api import get
from rich.console import Console
console = Console()

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3N1ZXIiOiJoYWNrc3RyYXAiLCJhdWRpZW5jZSI6Imh0dHBzOi8vaGFja3N0cmFwLmNvbSIsImFsZ29yaXRobXMiOlsiSFMyNTYiXSwiY2xhaW1zIjp7Im9yZyI6ImhhY2tzdHJhcCJ9LCJpYXQiOjE2MjQ3MDM0MDh9.bucqSg6pMXsag5wsHBSucUjl3rtCAZV9pKasC-M_04k"
base_url = 'https://blink.hackstrap.com/'

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World'


@app.route('/unity')
def unity():
    return 'Welcome to Unity'


@app.route('/unity/v1')
def v1():
    return 'List of v1 endpoints'


@app.route('/unity/v1/total_revenue', methods=['GET'])
def total_revenue():
    try:
        response = requests.get(base_url + "v1/revenue/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  
    except Exception as err:
        print(f'Other error occurred: {err}')  
    else:
        print('Success!')
    result = requests.get(base_url + "v1/revenue/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_revenue"] = data["total_mrr"] + data["total_non_recurring_revenue"]
    data = data.to_dict('records')
    #console.log(json.dumps(data), log_locals=True)
    data = json.dumps(data)
    return data

@app.route('/unity/v1/total_revenue_gr', methods=['GET'])
def total_revenue_gr():
    result = requests.get(base_url + "v1/revenue/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_revenue"] = data["total_mrr"] + data["total_non_recurring_revenue"]
    data["total_revenue_gr"] = data["total_revenue"].pct_change().fillna(0).round(3) * 100
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_mrr_gr', methods=['GET'])
def total_mrr_gr():
    result = requests.get(base_url + "v1/revenue/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_mrr_gr"] = data["total_mrr"].pct_change().fillna(0).round(3) * 100
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_customer_support_expenses', methods=['GET'])
def total_customer_support_expenses():
    result = requests.get(base_url + "v1/expense/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_customer_support_expenses"] = data["total_payroll_support"] + data["software_and_tools_support"]
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_service_delivery_expenses', methods=['GET'])
def total_service_delivery_expenses():
    result = requests.get(base_url + "v1/expense/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_service_delivery_expenses"] = data["hosting_service_delivery"]
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_cost_of_goods_manufactured', methods=['GET'])
def total_cost_of_goods_manufactured():
    result = requests.get(base_url + "v1/expense/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_cost_of_goods_manufactured"] = data["direct_material_costs"] + data["direct_labor_costs"] + data["manufacturing_overhead"] + data["net_wip_inventory"]    
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_cogs', methods=['GET'])
def total_cogs():
    result = requests.get(base_url + "v1/expense/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_customer_support_expenses"] = data["total_payroll_support"] + data["software_and_tools_support"]
    data["total_service_delivery_expenses"] = data["hosting_service_delivery"]
    data["total_cost_of_goods_manufactured"] = data["direct_material_costs"] + data["direct_labor_costs"] + data["manufacturing_overhead"] + data["net_wip_inventory"]
    data["total_cogs"] = data["total_cost_of_goods_manufactured"] + data["net_finished_goods_inventory"] + data["total_other_cogs"]
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_opex_expenses', methods=['GET'])
def total_opex_expenses():
    result = requests.get(base_url + "v1/opex/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_opex_expenses"] = data["total_general_and_administrative_expenses"] + data["total_sales_and_marketing_expenses"] + data["total_research_and_development_expenses"]
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_customers', methods=['GET'])
def total_customers():
    result = requests.get(base_url + "v1/users/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_customers"] = data["total_customers_at_beginning_of_month"] + data["total_new_customers_acquired"] - data["total_customers_churned"]
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/total_monthly_active_users_gr', methods=['GET'])
def total_monthly_active_users_gr():
    result = requests.get(base_url + "v1/users/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["total_monthly_active_users_gr"] = data["total_monthly_active_users"].pct_change().fillna(0).round(3) * 100
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/customer_churn_rate', methods=['GET'])
def customer_churn_rate():
    result = requests.get(base_url + "v1/users/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data["customer_churn_rate"] = (data["total_customers_churned"]/data["total_customers_at_beginning_of_month"]).fillna(0).round(3) * 100    
    data = data.to_dict('records')
    data = json.dumps(data)
    return data


@app.route('/unity/v1/gross_profit_margin', methods=['GET'])
def gross_profit_margin():
    revenue = requests.get(base_url + "v1/revenue/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    expense = requests.get(base_url + "v1/expense/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    revenue = json.loads(revenue.text)
    revenue = pd.DataFrame(revenue)
    expense = json.loads(expense.text)
    expense = pd.DataFrame(expense)
    revenue["total_revenue"] = revenue["total_mrr"] + revenue["total_non_recurring_revenue"]
    expense["total_customer_support_expenses"] = expense["total_payroll_support"] + expense["software_and_tools_support"]
    expense["total_service_delivery_expenses"] = expense["hosting_service_delivery"]
    expense["total_cost_of_goods_manufactured"] = expense["direct_material_costs"] + expense["direct_labor_costs"] + expense["manufacturing_overhead"] + expense["net_wip_inventory"]
    expense["total_cogs"] = expense["total_cost_of_goods_manufactured"] + expense["net_finished_goods_inventory"] + expense["total_other_cogs"]
    revenue["gross_profit_margin"] = ((revenue["total_revenue"] - expense["total_cogs"])/revenue["total_revenue"]).round(3) * 100
    revenue = revenue.to_json(orient='records')
    return revenue


@app.route('/unity/v1/customer_acquisition_cost', methods=['GET'])
def customer_acquisition_cost():
    users = requests.get(base_url + "v1/users/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    opex = requests.get(base_url + "v1/opex/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    users = json.loads(users.text)
    users = pd.DataFrame(users)
    opex = json.loads(opex.text)
    opex = pd.DataFrame(opex)
    users["customer_acquisition_cost"] = (opex["total_sales_and_marketing_expenses"]/users["total_new_customers_acquired"]).round(3)
    users = users.to_json(orient='records')
    return users


@app.route('/unity/v1/ltv_to_cac_ratio', methods=['GET'])
def ltv_to_cac_ratio():
    revenue = requests.get(base_url + "v1/revenue/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    users = requests.get(base_url + "v1/users/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    opex = requests.get(base_url + "v1/opex/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    revenue = json.loads(revenue.text)
    revenue = pd.DataFrame(revenue)
    users = json.loads(users.text)
    users = pd.DataFrame(users)
    opex = json.loads(opex.text)
    opex = pd.DataFrame(opex)
    users["customer_churn_rate"] = (users["total_customers_churned"]/users["total_customers_at_beginning_of_month"]).fillna(0).round(3) * 100
    users["customer_acquisition_cost"] = (opex["total_sales_and_marketing_expenses"]/users["total_new_customers_acquired"]).round(3)
    users["customer_lifetime_value"] = (revenue["total_mrr"]/((users["total_customers_at_beginning_of_month"] + users["total_new_customers_acquired"] - users["total_customers_churned"]) * ((users["total_customers_churned"]/users["total_customers_at_beginning_of_month"])).fillna(0).round(3) * 100)).round(3)
    users["ltv_to_cac_ratio"] = (users["customer_lifetime_value"]/users["customer_acquisition_cost"]).round(3)
    users = users.to_json(orient='records')
    return users


@app.route('/unity/v1/investment_total', methods=['GET'])
def investment_total():
    result = requests.get(base_url + "v1/investment/?page=0&page_size=12",
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data = pd.DataFrame(data.groupby(by=['investor_id'])['amount'].sum())
    data = data.to_dict()
    data = json.dumps(data)
    return data


@app.route('/unity/v1/startups_invested', methods=['GET'])
def startups_invested():
    result = requests.get(base_url + "v1/investment/?page=0&page_size=30",
        headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data = data.groupby(by=['investor_id'])["startup_id"].unique()
    data = data.to_json(orient='index')
    return data


@app.route('/unity/v1/investments_month', methods=['GET'])
def investments_month():
    result = requests.get(base_url + "v1/investment/?page=0&page_size=30",
        headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)})
    data = json.loads(result.text)
    data = pd.DataFrame(data)
    data = data.groupby(by=['investor_id','year','month'])['amount'].sum()
    data = data.reset_index().to_json(orient='records')
    return data


#export FLASK_ENV=development 
if __name__ == '__main__':
    app.run()