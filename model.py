from datetime import datetime
from app import db
import hashlib
from flask import session

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
		self.password = make_pw_hash(password)


def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True
    return False

def existing_user(username):
	if User.query.filter_by(username=username).first():
		return True
	return False

def set_user(user):
	if existing_user(user):
		return user.username
	return False

def add_user(username,password):	
	user = User(username,password)
	db.session.add(user)
	db.session.commit()
	session['username'] = user.username

def all_active_blogs():
	return Blog.query.order_by(Blog.post_date.desc()).all()

def get_blog_post(id):
	return Blog.query.get(id)