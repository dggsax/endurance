#!/usr/bin/python
activate_this = "/opt/endurance/venv/bin/activate_this.py"
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, "/opt/endurance")

from web import app as application

if __name__ == "__main__":
	application.run()