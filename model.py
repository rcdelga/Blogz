from app import app, db
from datetime import datetime

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.Text)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_date = db.Column(db.DateTime)
	deleted = db.Column(db.Boolean)

	def __init__(self,title,body,owner,post_date=None):
		self.title = title
		self.body = body
		self.owner = owner
		if post_date is None:
			post_date = datetime.now()
		self.post_date = post_date
		self.deleted = False
	def __repr__(self):
		# return '<Post %r>' % self.title
		return "<Blog(id='%r' title='%r' owner='%r')>" % (self.id,self.title,self.owner)

class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(120),unique=True)
	password = db.Column(db.String(120))
	blogs = db.relationship('Blog', backref='owner')

	def __init__(self,username,password):
		self.username = username
		self.password = password