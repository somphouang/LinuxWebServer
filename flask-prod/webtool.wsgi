#!/usr/bin/python
import sys
sys.path.append('/var/www/flask-prod/ItemCatalog/')
from app import app as application

application.secret_key = 'IoTXcD7rzRs9GcYcHbcDESPm'
application.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://'
        'catalogitem:udacity@localhost/catalogitem')
