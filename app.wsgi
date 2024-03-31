#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/root/iit-gpt-backend')

activate_this = '/root/.local/share/virtualenvs/iit-gpt-backend-J7UA8vGR/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application
