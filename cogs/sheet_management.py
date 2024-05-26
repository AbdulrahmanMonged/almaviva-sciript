from . import secretvars
from datetime import datetime
import gspread
from .utility import resource_path

gc = gspread.service_account(filename=resource_path("account.json"))


def initialize_sheet(logged_user, logged_password):
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sh = gc.open("Almaviva-logs").sheet1
    response = sh.append_row([logged_user, logged_password, current_date])["updates"][
        "updatedRange"
    ]
    secretvars.ID = int(response.split(":")[-1][1:])
    secretvars.FIRST_RUN = True


def start_excution(site_name, site_password):
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sh = gc.open("Almaviva-logs").sheet1
    sh.update_cell(secretvars.ID, 4, site_name)
    sh.update_cell(secretvars.ID, 5, site_password)
    sh.update_cell(secretvars.ID, 7, current_date)


def update_login_status(status):
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sh = gc.open("Almaviva-logs").sheet1
    sh.update_cell(secretvars.ID, 6, current_date)
    sh.update_cell(secretvars.ID, 8, status)
    sh.update_cell(secretvars.ID, 9, "Waiting...")


def update_operation_status(status):
    sh = gc.open("Almaviva-logs").sheet1
    sh.update_cell(secretvars.ID, 9, status)


def payment_gate_link(link):
    sh = gc.open("Almaviva-logs").sheet1
    sh.update_cell(secretvars.ID, 10, link)


def logout():
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sh = gc.open("Almaviva-logs").sheet1
    sh.update_cell(secretvars.ID, 11, current_date)
    
def append_account(account):
    sh = gc.open("Almaviva-logs").sheet1
    val = sh.cell(secretvars.ID, 12).value
    new_val = val + " - " + account if val else account
    sh.update_cell(secretvars.ID, 12, new_val)
