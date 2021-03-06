import os
import hflasker
import unittest
import tempfile

class HFlaskerTestCase(unittest.TestCase):

	def setUp(self):
		self.db_fd, hflasker.app.config['DATABASE'] = tempfile.mkstemp()
		hflasker.app.config['TESTING'] = True
		self.app = hflasker.app.test_client()
		with hflasker.app.app_context():
			hflasker.init_db()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(hflasker.app.config['DATABASE'])

	def test_empty_db(self):
		rv = self.app.get('/')
		assert b'No entries here so far' in rv.data

	def login(self, username, password):
		return self.app.post('/login', data=dict(
			username=username,
			password=password
			), follow_redirects=True)

	def logout(self):
		return self.app.get('/logout', follow_redirects=True)

	def test_login_logout(self):
		rv = self.login('admin', 'password')
		assert b'You were logged in' in rv.data
		rv = self.logout()
		assert b'You were logged out' in rv.data
		rv = self.login('adminx', 'passowrd')
		assert b'Invalid username' in rv.data
		rv = self.login('admin', 'passwords')
		assert b'Invalid password' in rv.data

	def test_messages(self):
		self.login('admin', 'password')
		rv = self.app.post('/add', data=dict(
			title='<Hello>',
			text='<strong>HTML</strong> allowed here'
			), follow_redirects=True)
		assert b'No entries here so far' not in rv.data
		assert b'&lt;Hello&gt;' in rv.data
		assert b'<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
	unittest.main()
