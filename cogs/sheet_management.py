import requests
from . import secretvars
from datetime import datetime

ENDPOINT = "https://api.sheety.co/2c40846f41f1ee967444320646c06b9e/almavivaLogs/main"
headers = {
    "Authorization": f"Bearer {secretvars.AUTH_CODE}",
    "Content-Type": "application/json",
}
current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def initialize_sheet(logged_user, logged_password):
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    body = {
        "main": {
            "loggedUser": logged_user,
            "loggedPassword": logged_password,
            "loginDate": current_date,
        }
    }
    response = requests.post(ENDPOINT, json=body)
    secretvars.ID = response.json()["main"]["id"]


def start_excution(site_name, site_password):
    ENDPOINT_ID = f"https://api.sheety.co/2c40846f41f1ee967444320646c06b9e/almavivaLogs/main/{secretvars.ID}"
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    body = {
        "main": {
            "loggedSiteAccount": site_name,
            "loggedSitePassword": site_password,
            "operationTimeExcution": current_date,
        }
    }
    requests.put(ENDPOINT_ID, json=body)


def update_login_status(status):
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ENDPOINT_ID = f"https://api.sheety.co/2c40846f41f1ee967444320646c06b9e/almavivaLogs/main/{secretvars.ID}"
    body = {
        "main": {
            "siteLoginDate": current_date,
            "loginStatus": status,
            "statusOfTheOperation": "Stuck on appointment Page",
        }
    }
    requests.put(ENDPOINT_ID, json=body)


def update_operation_status(status):
    ENDPOINT_ID = f"https://api.sheety.co/2c40846f41f1ee967444320646c06b9e/almavivaLogs/main/{secretvars.ID}"
    body = {"main": {"statusOfTheOperation": status}}
    requests.put(ENDPOINT_ID, json=body)
