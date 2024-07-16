from cogs.login_gui import App
from cogs import secretvars
import sys

app = App()
app.mainloop()

secretvars.MAIN_FLAG = 0
sys.exit()
