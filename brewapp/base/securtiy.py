import inspect
import logging
import os
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

import flask_restless
from flask import (Flask, Response, abort, redirect, render_template, request,
                   url_for)
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

from _thread import start_new_thread
from brewapp import app

## SECURTIY

def requires_auth(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@requires_auth
def detect_user_language():
    pass

def check_auth(username, password):
    return username == app.brewapp_config["USERNAME"] and password == app.brewapp_config["PASSWORD"]

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})
