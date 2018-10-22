from model import Blog, User, get_blog_post, add_user, existing_user, get_all_users, make_pw_hash
from flask import request, redirect, render_template, flash, make_response, session
from app import app, db


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
		entries = {'username':request.form['username'],
					'password1':request.form['password1'],
					'password2':request.form['password2']}
		errors = {'username_error':'',
				'password1_error':'',
				'password2_error':''}
		for entry in entries:
			if not 2 < len(entries[entry]) < 21 and ' ' not in entries[entry]:
				errors[entry+'_error'] = "Invalid Entry: Requires 2-20 characters with no spaces."
				if entry == 'username':
					entries[entry] = ''
		if entries['password1'] != entries['password2']:
			error = "Passwords do not match."
			errors['password1_error'] = error
			errors['password2_error'] = error
		if existing_user(entries['username']):
			errors['username_error'] = "[{0}] is already registered.".format(entries['username'])
			entries['username'] = ''
		for entry in errors:
			if errors[entry]:
				entries['password1'] = ''
				entries['password2'] = ''
				return render_template('signup.html', **entries, **errors)
		add_user(entries['username'],entries['password1'])
		session['username'] = entries['username']
		return redirect('/blog')	
	return render_template('signup.html')


@app.route('/login',methods=['GET','POST'])
def login():

	if request.method == 'POST':
		# entries = {'username':request.form['username'], 'password':request.form['password']}
		# errors = {'username_error':'','password_error':''}
		
		username = request.form['username']
		password = make_pw_hash(request.form['password'])
		u_error = ''
		pw_error = ''

		user = existing_user(username)

		if not user:
			u_error = "[{0}] not a registered user.".format(username)
			username = ''
		if user and user.password != password:
			pw_error = "Error: Password incorrect."		
		if not u_error and not pw_error and user and password == user.password:
			session['username'] = username
			flash("Success! Logged in!")
			return redirect('/newpost')
		return render_template("login.html",username=username,u_error=u_error,pw_error=pw_error)
	return render_template("login.html")


@app.route("/")
def index():
	return render_template('index.html',user_list=get_all_users())


@app.route("/blog")
def blog():
	count = int(request.cookies.get('visit-count', 0))
	count += 1
	message = "You have visited this page {0} time(s).".format(str(count))

	# resp = make_response(message)
	# resp.set_cookie('visit-count', str(count))
	# return resp

	bid = request.args.get('id')

	page = request.args.get('page', 1, type=int)
	blogs = Blog.query.order_by(Blog.post_date.desc()).paginate(per_page=3)

	if bid:
		return render_template('id.html',post=get_blog_post(bid))
	resp = make_response(render_template('blog.html',blogs=blogs))
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


@app.route("/newpost", methods=['GET','POST'])
def newpost():

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

	if request.method == 'POST':
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
		return render_template("newpost.html",new_blog_title=new_title,new_title_error=new_title_error,new_blog_body=new_body,new_body_error=new_body_error)
	return render_template('newpost.html')

@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect('login')

if __name__ == "__main__":
	app.run()