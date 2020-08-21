from flask import Blueprint

from .. import socketio


base = Blueprint(
    'base',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@socketio.on('connect', namespace='/brew')
def ws_connect():
    print("WS-CONNECT")
