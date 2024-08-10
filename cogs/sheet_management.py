from datetime import datetime
from uuid import uuid4
import psycopg
from datetime import datetime
import asyncio
import socket
from . import secretvars
import json
from .colors import *

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

    async def check_passport(self):
        try:
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    await curr.execute(
                        "UPDATE operations SET is_passport_exists = %s WHERE id = %s",
                        (
                            True,
                            self.key,
                        ),
                    )
                    await db.commit()
        except Exception as e:
            print(e)
            await self.check_passport()

    async def save_account(self, window, name):
        try:
            window.disable_customer_display()
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    key = uuid4()
                    await curr.execute(
                        "INSERT INTO customers (id, owner_id, jsondata, name) values (%s, %s, %s, %s)",
                        (
                            key,
                            secretvars.owner_id,
                            json.dumps(secretvars.data),
                            name,
                        ),
                    )
                    await db.commit()
                    window.print_in_log(
                        "تم حفظ العميل تحت اسم {0} بنجاح".format(name), color=success
                    )
                    window.enable_customer_display()
                    window.refresh_customer_display()
                    secretvars.customer_id = key
        except Exception as e:
            window.enable_customer_display()
            window.print_in_log(
                "تعذر حفظ العميل تحت اسم {0}".format(name), color=danger
            )
            print(e)

    async def get_accounts(self, window):
        try:
            window.customers_display.forgeT_all_componoents()
            window.customers_display.show_spinner()
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    if secretvars.is_admin:
                        await curr.execute(
                            "SELECT * FROM customers",
                        )
                    else:
                        await curr.execute(
                            "SELECT * FROM customers where owner_id = %s",
                            (secretvars.owner_id,),
                        )
                    data = await curr.fetchall()
                    window.customers_display.customers = []

                    for customer in data:
                        customer_data = customer[2]
                        if secretvars.is_admin:
                            if (
                                customer_data["accepted"]
                                and not customer_data["booked"]
                                and customer[1] != secretvars.owner_id
                            ):
                                window.customers_display.add_customer(
                                    customer[3],
                                    customer[1],
                                    customer[0],
                                    customer_data["accepted"],
                                    False,
                                )
                            elif customer[1] == secretvars.owner_id:
                                window.customers_display.add_customer(
                                    customer[3],
                                    customer[1],
                                    customer[0],
                                    customer_data["accepted"],
                                    customer_data["booked"],
                                )
                        else:
                            window.customers_display.add_customer(
                                customer[3],
                                customer[1],
                                customer[0],
                                customer_data["accepted"],
                                customer_data["booked"],
                            )
                    window.after(500, window.customers_display.refresh)

        except Exception as e:
            print(e)

    async def get_data_of_account(self, window, id):
        try:
            window.disable_customer_display()
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    if secretvars.is_admin:
                        await curr.execute(
                            "SELECT * FROM customers where id = %s",
                            (id,),
                        )
                    else:
                        await curr.execute(
                            "SELECT * FROM customers where id = %s and owner_id = %s",
                            (
                                id,
                                secretvars.owner_id,
                            ),
                        )
                    customer = await curr.fetchone()
                    window.load_data(customer[2])
                    secretvars.data = dict(customer[2])
                    window.enable_customer_display()
                    secretvars.customer_id = customer[0]

        except Exception as e:
            window.enable_customer_display()
            print(e)

    async def update_account(self, window, name):
        try:
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    if secretvars.customer_id:
                        await curr.execute(
                            "UPDATE customers set jsondata = %s where id = %s and owner_id = %s",
                            (
                                json.dumps(secretvars.data),
                                secretvars.customer_id,
                                secretvars.owner_id,
                            ),
                        )
                        await db.commit()
                    else:
                        await self.save_account(window, name)

        except Exception as e:
            print(e)

    async def delete_customer(self, window, customer_widget, id):
        try:
            window.disable_customer_display()
            async with await psycopg.AsyncConnection.connect(URI) as db:
                async with db.cursor() as curr:
                    await curr.execute(
                        "DELETE FROM customers where id = %s and owner_id = %s",
                        (
                            id,
                            secretvars.owner_id,
                        ),
                    )
                    await db.commit()
                    window.print_in_log("تم حذف العميل بنجاح", color=success)
                    window.enable_customer_display()
                    customer_widget.destroy()
                    # window.refresh_customer_display()
                    # window.customers_display.refresh()
        except Exception as e:
            window.enable_customer_display()
            print(e)


db = dbManagement()
