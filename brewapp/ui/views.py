from datetime import datetime
from functools import update_wrapper, wraps

from flask import Blueprint, jsonify, make_response, render_template, request

from brewapp import app, socketio
from brewapp.base.model import *

ui = Blueprint('ui', __name__, template_folder='templates', static_folder='static')


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

@ui.route('/')
@nocache
def index():
    return ui.send_static_file("index.html")
    '''
    if app.brewapp_config.get("SETUP", "Yes") == "Yes":
        app.logger.info("SHOW SETUP HTML")
        return ui.send_static_file("setup.html")
    else:
        app.logger.info("SHOW INDEX HTML")
        return ui.send_static_file("index.html")
    '''
