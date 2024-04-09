import sys
sys.path.insert(0, '/var/www/prod-iit-gpt-backend')
sys.path.insert(0, '/var/www/prod-iit-gpt-backend/persist')

activate_this = '/var/www/prod-iit-gpt-backend/virtualenvs/iit-gpt-backend-prod-4QCb9T1x/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from server import app as application
