


__author__ = 'xlonga Huang'

'''
JSON API definition
'''

import json, logging, inspect, functools

class APIError(Exception):
	'''
	the base APIError which contains error(required), data(optional) and message(option).
	'''
	def __init__(self, error, data='', message=''):
		super(APIError, self).__init__(message)
		self.error = error
		self.data = data
		self.message = message

class APIValueError(APIError):
	'''
	Indicate thr inpit value has errror or invalid. The data specifies the errpr field of input form.
	'''
	def __init__(self, field, message=''):
		super(APIValueError, self).__init__('value:invalid', field, message)

class APIResourceNotFoundError(APIError):
	'''
	Indicate the resource was not found. The data specifies the resource1 name.
	'''
	def __init__(self, field, message=''):
		super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)

class APIPermssionError(APIError):
	'''
	Indicate the api has no permisson.
	'''
	def __init__(self, message=''):
		super(APIPermssionError, self).__init__('permisson；forbidden', 'permisson', message)