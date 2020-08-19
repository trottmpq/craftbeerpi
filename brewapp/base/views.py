from flask import Blueprint

from brewapp import app, socketio
from brewapp.base.model import *
from brewapp.base.util import *

base = Blueprint(
    'base',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@socketio.on('connect', namespace='/brew')
def ws_connect():
    print("WS-CONNECT")
