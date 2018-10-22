from datetime import datetime
from app import db
import hashlib
import random
import string

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
		return "<Blog %r %r by %r>" % (self.id,self.title,self.owner.username)

class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(120),unique=True)
	password = db.Column(db.String(120))
	blogs = db.relationship('Blog', backref='owner')

	def __init__(self,username,password):
		self.username = username
		self.password = make_pw_hash(password)

	def __repr__(self):
		return "<User %r %r>" % (self.id, self.username)


def make_salt():
	return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_pw_hash(password, salt=None):
	if not salt:
		salt = make_salt()
	hash = hashlib.sha256(str.encode(password)).hexdigest()
	return '{0},{1}'.format(hash, salt)

def check_pw_hash(password, hash):
	salt = hash.split(',')[1]
	if make_pw_hash(password, salt) == hash:
		return True
	return False

def existing_user(username):
	return User.query.filter_by(username=username).first()

def add_user(username,password):	
	db.session.add(User(username,password))
	db.session.commit()

def all_active_blogs():
	return Blog.query.order_by(Blog.post_date.desc()).all()

def get_blog_post(id):
	return Blog.query.get(id)

def get_all_users():
	return User.query.all()