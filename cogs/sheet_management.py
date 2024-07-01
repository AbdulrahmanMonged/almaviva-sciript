from datetime import datetime
from uuid import uuid4
import psycopg
from datetime import datetime
import asyncio
import socket

URI = "postgresql://AbdulrahmanMonged:pnZyGIo96qhe@ep-lucky-tree-44958310-pooler.eu-central-1.aws.neon.tech/almaviva_db?sslmode=require"
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class dbManagement:
    def __init__(self):
        self.db = None
        self.curr = None
        self.key = None
        self.first_run = True
        asyncio.run(self.init_connection())

    async def init_connection(self):
        self.db = await psycopg.AsyncConnection.connect(URI)
        self.curr = self.db.cursor()

    async def start_excution(self, logged_user, logged_password):
        try:
            self.key = uuid4()
            await self.curr.execute(
                "INSERT INTO operations (id, username, password, program_login_time, IP) VALUES (%s ,%s, %s, %s, %s)",
                (
                    self.key,
                    logged_user,
                    logged_password,
                    datetime.now(),
                    socket.gethostbyname(socket.gethostname()),
                ),
            )
            await self.db.commit()
        except Exception as e:
            print(e)
            await self.init_connection()
            await self.start_excution(logged_user, logged_password)

    async def finish_excution(self, paymentGate):
        try:
            await self.curr.execute(
                "UPDATE operations SET booking_time = %s, payment_gate = %s WHERE id = %s",
                (datetime.now(), paymentGate, self.key),
            )
            await self.db.commit()
            self.first_run = False
        except Exception as e:
            print(e)
            await self.init_connection()
            await self.finish_excution(paymentGate)
    
    async def write_user(self, siteName, sitePassword):
        try:
            if not (self.first_run):
                await self.curr.execute(
                    "SELECT * FROM operations WHERE id = %s", (self.key,)
                )
                user = await self.curr.fetchone()
                await self.start_excution(user[1], user[2])
            await self.curr.execute(
                "UPDATE operations SET site_username = %s, site_password = %s WHERE id = %s",
                (siteName, sitePassword, self.key),
            )
            await self.db.commit()
        except Exception as e:
            print(e)
            await self.init_connection()
            await self.write_user(siteName, sitePassword)

    async def close_connection(self):
        await self.db.close()


db = dbManagement()
