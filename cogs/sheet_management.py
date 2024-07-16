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
        self.key = None
        self.first_run = True

    async def start_excution(self, logged_user, logged_password):
        try:
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    self.key = uuid4()
                    await curr.execute(
                        "INSERT INTO operations (id, username, password, program_login_time, IP) VALUES (%s ,%s, %s, %s, %s)",
                        (
                            self.key,
                            logged_user,
                            logged_password,
                            datetime.now(),
                            socket.gethostbyname(socket.gethostname()),
                        ),
                    )
                    await db.commit()
        except Exception as e:
            print(e)
            await self.init_connection()
            await self.start_excution(logged_user, logged_password)

    async def finish_excution(self, paymentGate):
        try:
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    await curr.execute(
                        "UPDATE operations SET booking_time = %s, payment_gate = %s WHERE id = %s",
                        (datetime.now(), paymentGate, self.key),
                    )
                    await db.commit()
                    self.first_run = False
        except Exception as e:
            print(e)
            await self.finish_excution(paymentGate)

    async def write_user(self, siteName, sitePassword):
        try:
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    if not (self.first_run):
                        await curr.execute(
                            "SELECT * FROM operations WHERE id = %s", (self.key,)
                        )
                        user = await curr.fetchone()
                        await self.start_excution(user[1], user[2])
                    await curr.execute(
                        "UPDATE operations SET site_username = %s, site_password = %s WHERE id = %s",
                        (siteName, sitePassword, self.key),
                    )
                    await db.commit()
        except Exception as e:
            print(e)
            await self.write_user(siteName, sitePassword)


db = dbManagement()
