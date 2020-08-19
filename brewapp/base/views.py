import json

from flask import Blueprint, jsonify, redirect, render_template, url_for

from brewapp import app, socketio

from .model import *
from .util import *

base = Blueprint('base', __name__, template_folder='templates', static_folder='static')

@socketio.on('connect', namespace='/brew')
def ws_connect():
    print("WS-CONNECT")
