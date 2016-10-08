# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'hflaskr.db'),
	SECRET_KEY='123456',
	USERNAME='admin',
	PASSWORD='password'
	)
)
app.config.from_envvar('HFLASKR_SETTINGS', silent=True)

# Connects to the specific database.
def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

# Opens a new database connection if there is none yet for
# the current application context.
def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

# Closes the database again at the end of the request.
@app.teardown_appcontext
def close_db():
	if hasattr(g, 'sqlite_db')
		g.sqlite_db.close()
