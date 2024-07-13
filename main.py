from cogs.login_gui import App
from cogs import secretvars
from cogs.sheet_management import db
import sys
import asyncio

app = App()
app.mainloop()

secretvars.MAIN_FLAG = 0
asyncio.run(db.close_connection())
sys.exit()
 