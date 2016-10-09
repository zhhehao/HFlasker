# -*- coding: utf-8 -*-
# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash
import hashlib
from datetime import datetime

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'hflaskr.db'),
	SECRET_KEY='\x00\xd8h(Z\x17\x8d\xb5\x97l\x88x0\xf2\xb3\xdcfU\xdb\x1f\x8d\x0b\xafk',
	USERNAME='',
	PASSWORD=''
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
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

# Initializes the database.
@app.cli.command('initdb')
def initdb_command():
	init_db()
	print('Initialized the database.')

# Show entries
@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, date, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

# Add entries
@app.route('/add', methods=['POST'])
def add_entry():
		if not session.get('logged_in'):
			abort(401)
		# generate timestamp
		submit_time = str(datetime.now().strftime("%A, %d.%B %Y %I:%M%p"))
		db = get_db()
		db.execute('insert into entries (title, date, text) values (?, ?, ?)', [request.form['title'], submit_time, request.form['text']])
		db.commit()
		flash('New entry was successfully posted.')
		return redirect(url_for('show_entries'))

# Login and logout
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		# generate sha1 value from user enter
		sha1 = hashlib.sha1()
		sha1.update(request.form['password'].encode('utf-8'))
		enter_password = sha1.hexdigest()
		# authorization check
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif enter_password != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))
