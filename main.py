from flask import Flask, request, redirect, render_template, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

def all_active_blogs():
	return Blog.query.order_by(Blog.post_date.desc()).all()

def get_blog_post(id):
	return Blog.query.get(id)

def valid_title(data):
	if 0 < len(data) < 121:
		return True
	else:
		return False

def valid_body(data):
	if 0 < len(data):
		return True
	else:
		return False

def valid_entry(data):
	if 2 < len(data) < 21 and " " not in data:
		return True
	else:
		return False

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

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


@app.before_request
def require_login():
	allowed_routes = ['login','signup','blog','index','singleUser']
	if (request.endpoint not in allowed_routes
		and '/static/' not in request.path
		and 'username' not in session):
		return redirect('/login')


@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method == 'POST':
		username = request.form['username']
		password1 = request.form['password1']
		password2 = request.form['password2']

		username_error = ''
		password1_error = ''
		password2_error= ''

		entry_error = "Entry not valid. (3-20 characters with no spaces)"
		pass_error = "Passwords do not match."
		registry_error = "[{0}] is already registered."

		if not valid_entry(username):
			username = ''
			username_error = entry_error
		if not valid_entry(password1):
			password1_error = entry_error
		if not valid_entry(password2):
			password2_error = entry_error
		if  password1 != password2:
			password1_error = pass_error
			password2_error = pass_error
		if not username_error and not password1_error and not password2_error:
			existing_user = User.query.filter_by(username=username).first()			
			if not existing_user:
				user = User(username=username,password=password1)
				db.session.add(user)
				db.session.commit()
				session['username'] = user.username
				return redirect('/blog')
			else:
				username_error = registry_error.format(username)
				username = ''	
		return render_template('signup.html',username=username,username_error=username_error,password1_error=password1_error,password2_error=password2_error)
	else:
		return render_template('signup.html')


@app.route('/login',methods=['GET','POST'])
def login():

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		u_error = ''
		pw_error = ''

		user = User.query.filter_by(username=username).first()

		if not user:
			u_error = "[{0}] not a registered user.".format(username)
			username = ''
		if user and user.password != password:
			pw_error = "Error: Password incorrect."		
		if not u_error and not pw_error and user and user.password == password:
			session['username'] = username
			flash("Success! Logged in!")
			return redirect('/newpost')
		else:
			return render_template("login.html",username=username,u_error=u_error,pw_error=pw_error)

	return render_template("login.html")


@app.route("/")
def index():
	user_list = User.query.all()
	return render_template('index.html',user_list=user_list)

@app.route("/blog")
def blog():
	count = int(request.cookies.get('visit-count', 0))
	count += 1
	message = "You have visited this page {0} time(s).".format(str(count))

	# resp = make_response(message)
	# resp.set_cookie('visit-count', str(count))
	# return resp

	bid = request.args.get('id')

	if bid:
		return render_template('id.html',post=get_blog_post(bid))
	else:
		resp = make_response(render_template('blog.html',blogs=all_active_blogs(),message=message))
		resp.set_cookie('visit-count', str(count))
		return resp



@app.route('/singleUser')
def singleUser():
	uid = request.args.get('uid')

	if uid:
		user = User.query.filter_by(id=uid).first()
		uid_list = Blog.query.filter_by(owner_id=uid).order_by(Blog.post_date.desc()).all()
		return render_template('singleUser.html',user=user,blogs=uid_list)
	else:
		return redirect('/')


@app.route("/newpost")
def new_post():
	return render_template('newpost.html')


@app.route("/add_blog", methods=['POST'])
def add_post():
	new_title = request.form['new_blog_title']
	new_body = request.form['new_blog_body']

	new_title_error = ''
	new_body_error = ''

	blank_error = "Blank Entry: Please fill out empty field."

	if not valid_title(new_title):
		new_title_error = blank_error
	if not valid_body(new_body):
		new_body_error = blank_error
	if not new_title_error and not new_body_error:
		user = User.query.filter_by(username=session['username']).first()
		new_blog = Blog(new_title,new_body,user)
		db.session.add(new_blog)
		db.session.commit()
		new_id = Blog.query.filter_by(title=new_title,body=new_body).first().id
		return redirect("/blog?id={0}".format(new_id))
	else:
		return render_template("newpost.html",new_blog_title=new_title,new_title_error=new_title_error,new_blog_body=new_body,new_body_error=new_body_error)


@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect('login')



app.secret_key = "blogz"

if __name__ == "__main__":
	app.run()