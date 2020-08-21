from flask import Blueprint

from .. import socketio
from .model import *
from .util import *

base = Blueprint(
    'base',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@socketio.on('connect', namespace='/brew')
def ws_connect():
    print("WS-CONNECT")
