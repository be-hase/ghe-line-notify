# -*- coding: utf-8 -*-

import errno
import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension


def mkdir_p(path):
    """same as mkdir -p command"""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


app = Flask(__name__)

app.config.from_pyfile('config.py')

database_uri = app.config['GHE_LN_DATABASE_URI']

if not database_uri:
    database_uri = os.getenv('DATABASE_URL', None)  # for Heroku PostgresSql addon

if not database_uri:
    # Default is using sqlite. and create db at "~/.ghe-line-notify/app.db"
    sqlite_db = os.path.expanduser('~{sep}.ghe-line-notify{sep}app.db'.format(sep=os.sep))
    mkdir_p(os.path.dirname(sqlite_db))
    database_uri = 'sqlite:///' + sqlite_db

app.config.update(
    SQLALCHEMY_DATABASE_URI=database_uri
)

# this is enabled when DEBUG == True.
toolbar = DebugToolbarExtension(app)

from . import database
from . import models
from . import views
