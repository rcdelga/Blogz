from model import Blog

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
		
def make_pw_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_pw_hash(password, hash):
    if make_pw_hash(password) == hash:
        return True

    return False