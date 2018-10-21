from model import existing_user

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

def no_form_errors(form, form2):

	# Checking for matching passwords
	if form['password1'] != form['password2']:
		error = "Passwords do not match."
		form2['password1_error'] = error
		form2['password2_error'] = error

	# Checking all entries for valid length and no spaces
	for entry in form:
		if not 2 < len(form[entry]) < 21 and ' ' not in form[entry]:
			form2[entry+'_error'] = "Invalid Entry: Requires 2-20 characters with no spaces."
			if form[entry] == form['username']:
				form[entry] = ''

	# Checks if the username is already in the database
	if existing_user(form['username']):
		form2['username_error'] = "[{0}] is already registered.".format(form['username'])
		form['username'] = ''

	# If no errors are generated, then PASS
	for entry in form2:
		if form2[entry]:
			form['password1'] = ''
			form['password2'] = ''
			return False

	return True