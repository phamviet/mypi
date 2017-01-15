# -*- coding: utf-8 -*-

"""
mypi.core
~~~~~~~~~~~~
This module provides the core MyPi experience.
"""

import importlib
import json
import os

from flask import Flask, Response, request, render_template, jsonify, make_response, url_for

# Find the correct template folder when running from a different location
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder=tmpl_dir)


# -----------
# Middlewares
# -----------
@app.after_request
def set_cors_headers(response):
	response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
	response.headers['Access-Control-Allow-Credentials'] = 'true'

	if request.method == 'OPTIONS':
		# Both of these headers are only used for the "preflight request"
		# http://www.w3.org/TR/cors/#access-control-allow-methods-response-header
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
		response.headers['Access-Control-Max-Age'] = '3600'  # 1 hour cache
		if request.headers.get('Access-Control-Request-Headers') is not None:
			response.headers['Access-Control-Allow-Headers'] = request.headers['Access-Control-Request-Headers']
	return response


@app.route('/')
def index():
	"""Landing Page."""

	return render_template('index.html')


@app.route('/ip')
def ip():
	"""Returns Origin IP."""

	return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr))


@app.route('/cmd', methods=['GET', 'POST'])
def cmd():
	"""Abstract cmd route."""
	args = {}
	if request.method == 'POST':
		method_string = request.form['cmd']
		if request.form.get("args"):
			args = json.loads(request.form.get("args"))
	else:
		method_string = request.args.get('cmd')

	if '.' in method_string:
		method_string = __name__.split('.')[0]  + '.' + method_string
		modulename = '.'.join(method_string.split('.')[:-1])
		methodname = method_string.split('.')[-1]

		attr = getattr(importlib.import_module(modulename), methodname)

	else:
		attr = globals()[method_string]

	ret = {}
	try:
		ret = attr(**args)
	except Exception as ex:
		ret["error"] = ex.message

	if ret is None:
		ret = {}

	if isinstance(ret, str):
		ret = {
			"output": ret
		}

	return jsonify(ret)





