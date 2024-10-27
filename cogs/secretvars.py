import threading

URI = "postgresql://AbdulrahmanMonged:kqAw9KrH2pXj@ep-lucky-tree-44958310.eu-central-1.aws.neon.tech/almaviva_db?sslmode=require"
Thread_Pool: list[threading.Thread] = []
MAIN_FLAG = 1
owner_id = ""
data = {
    "users": [],
    "account_data": {},
    "media": {"passport": "", "nulla": "", "phoneNumber": ""},
    "office": "",
    "visa_price": "",
    "otp": "",
    "accepted": False,
    "booked": False,
}
customer_id = ""
is_admin = 0

username = ""
password = ""

ready_checking = {}
accounts = []