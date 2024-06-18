from datetime import datetime
from uuid import uuid4
import psycopg
from datetime import datetime
import asyncio
import socket
URI = "postgresql://AbdulrahmanMonged:YdDtzrB46JCU@ep-lucky-tree-44958310.eu-central-1.aws.neon.tech/almaviva_db?sslmode=require"
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class dbManagement:
    def __init__(self):
        self.db = None
        self.curr = None
        self.key = None
        self.first_run = False
        asyncio.run(self.init_connection())
    
    async def init_connection(self):
        self.db = await psycopg.AsyncConnection.connect(URI)
        self.curr = self.db.cursor()
    
    async def start_excution(self, logged_user, logged_password):
        self.key = uuid4()
        await self.curr.execute(
            "INSERT INTO operations (id, username, password, program_login_time, IP) VALUES (%s ,%s, %s, %s, %s)",
            (self.key ,logged_user, logged_password, datetime.now(), socket.gethostbyname(socket.gethostname())),
        )
        await self.db.commit()
        self.first_run = True
    async def finish_excution(self, siteName, sitePassword, paymentGate):
        await self.curr.execute(
            "UPDATE operations SET site_username = %s, site_password = %s, booking_time = %s, payment_gate = %s WHERE id = %s",
            (siteName, sitePassword, datetime.now(), paymentGate, self.key),
        )
        await self.db.commit()
    
    async def close_connection(self):
        await self.db.close()

db = dbManagement()
