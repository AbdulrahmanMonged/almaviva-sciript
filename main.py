from cogs.login_gui import App
from cogs import secretvars
from cogs.sheet_management import logout
import sys

app = App()
app.mainloop()

secretvars.MAIN_FLAG = 0
logout()

sys.exit()
