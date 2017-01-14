# -*- coding: utf-8 -*-

"""
httpbin.core
~~~~~~~~~~~~
This module provides the core HttpBin experience.
"""

import base64
import json
import os
import random
import time
import uuid
import argparse

from flask import Flask, Response, request, render_template, redirect, jsonify as flask_jsonify, make_response, url_for
from werkzeug.datastructures import WWWAuthenticate, MultiDict
from werkzeug.http import http_date
from werkzeug.wrappers import BaseResponse
from six.moves import range as xrange

ENV_COOKIES = (
	'_gauges_unique',
	'_gauges_unique_year',
	'_gauges_unique_month',
	'_gauges_unique_day',
	'_gauges_unique_hour',
	'__utmz',
	'__utma',
	'__utmb'
)


def jsonify(*args, **kwargs):
	response = flask_jsonify(*args, **kwargs)
	if not response.data.endswith(b'\n'):
		response.data += b'\n'
	return response


# Prevent WSGI from correcting the casing of the Location header
BaseResponse.autocorrect_location_header = False

# Find the correct template folder when running from a different location
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder=tmpl_dir)

# Set up Bugsnag exception tracking, if desired. To use Bugsnag, install the
# Bugsnag Python client with the command "pip install bugsnag", and set the
# environment variable BUGSNAG_API_KEY. You can also optionally set
# BUGSNAG_RELEASE_STAGE.
if os.environ.get("BUGSNAG_API_KEY") is not None:
	try:
		import bugsnag
		import bugsnag.flask

		release_stage = os.environ.get("BUGSNAG_RELEASE_STAGE") or "production"
		bugsnag.configure(api_key=os.environ.get("BUGSNAG_API_KEY"),
						  project_root=os.path.dirname(os.path.abspath(__file__)),
						  use_ssl=True, release_stage=release_stage,
						  ignore_classes=['werkzeug.exceptions.NotFound'])
		bugsnag.flask.handle_exceptions(app)
	except:
		app.logger.warning("Unable to initialize Bugsnag exception handling.")


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
def view_landing_page():
	"""Landing Page."""
	tracking_enabled = False
	return render_template('index.html', tracking_enabled=tracking_enabled)


@app.route('/ip')
def view_origin():
	"""Returns Origin IP."""

	return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr))


@app.route('/restart')
def restart():
	"""Restart device."""

	return jsonify(cmd="restart")


@app.route('/shutdown')
def shutdown():
	"""Shutdown device."""

	return jsonify(cmd="restart")
