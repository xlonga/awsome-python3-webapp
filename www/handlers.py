


__author__ = 'xlonga Huang'

'url handlers'

import re,time, json, logging, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import APIvalueError, APIresourceNotFoundError

from models import User, Comment, Blog, next_id
from config import configs

# @get('/')
# async def index(request):
# 	users = await User.findAll()
# 	return {
# 		'__template__': 'test.html',
# 		'users': users
# 	}

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

def user2cookie(user, max_age):
	'''
	Generate cookies str by user.
	'''
	#build cppkie string by: id-expires-shal
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires,hashlib.shal(s.encode('uft-8')).hexdigest()]
	return '-'.join(L)

@asyncio.coroutine
def cookie2user(cookie_str):
	'''
	Parsw cookie and load user if cookie is vaild.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		uid, expires, shal = L
		if int(expires) < time.time():
			return None
		user = await User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
		if shal != hashlib.shal(s.encode('uft-8')).hexdigest():
			logging.info('invaild shal')
			return None
		user.passwd = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None

@get('/')
def index(request):
	summary = 'Lorem ipsum dolor sit amet, consetetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
	blogs = [
		Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
		Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
		Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
	]
	return {
		'__template__': 'blogs.html',
		'blogs': blogs
	}

@get('/register')
def register():
	return {
		'__template__': 'register.html'
	}

@get('/signin')
def signin():
	return {
		'__template__': 'signin.html'
	}

@post('/api/authenticate')
def authenticate(*, email, passwd):
	if not email:
		raise APIvalueError('email', 'Invaild email.')
	if not passwd:
		raise APIvalueError('passwd', 'Invaild passwd.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIvalueError('email', 'Email not exist.')
	user = users[0]
	#check passwd
	shal = hashlib.shal()
	shal.update(user.id.encode('uft-8'))
	shal.update(b':')
	shal.update(passwd.encode('uft-8'))
	if user.passwd != shal.hexdigest():
		raise APIvalueError('passwd', 'Invaild password.')
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('uft-8')
	return r

@get('/signout')
def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return request

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHAL = re.compile(r'^[0-9a-f]{40}$')

@get('/api/users')
async def api_get_users(*, email, name, passwd):
	if not name or name.strip():
		raise APIvalueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIvalueError('email')
	if not passwd or not _RE_SHAL.match(passwd):
		raise APIvalueError('passwd')
	users = await User.findAll('email=?', [email])
	if len(users) > 0:
		raise APIError('register:failed', 'email', 'Email is already in use.')
	uid = next_id()
	shal_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.shal(shal_passwd.encode('uft-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('uft-8')).hexdigest())
	await user.save()
	# make session cookie:
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('uft-8')
	return r