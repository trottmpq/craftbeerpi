import json
import time

from flask import Blueprint, jsonify, render_template, request

from ... import app, db, socketio
from ..actor import *
from ..model import *
from ..model import Config
from ..util import *


class Automatic(object):

    configparameter = None
    config = None

    def isRunning(self):
        key = str(self.kid)+"pid"
        return app.brewapp_kettle_automatic[key]

    def getCurrentTemp(self):
        try:
            id = int(app.brewapp_kettle_state[self.kid]["sensorid"])
            return app.brewapp_thermometer_last[id]
        except:
            return None

    def getTargetTemp(self):
        return app.brewapp_kettle_state[self.kid]["target_temp"]

    def switchHeaterON(self):
        switchOn(app.brewapp_kettle_state[self.kid]["heater"])

    def switchHeaterOFF(self):
        switchOff(app.brewapp_kettle_state[self.kid]["heater"])

    def getConfig(self):
        pass

    def __init__(self, kid):
        self.kid = kid

@app.route('/api/automatic/paramter', methods=['GET'])
def automatic_parameters():
    result = []
    for i in app.brewapp_pid:
        result.append({"name":i.__name__, "parameter": i.configparameter})
    return json.dumps(result)

## STOP PID Controller
def stopPID(kid):
    key = str(kid)+"pid";
    app.brewapp_kettle_automatic[key] = False

## START PID Controller
def startAutomatic(kid):
    key = str(kid)+"pid"
    app.brewapp_kettle_automatic[key] = True
    t = socketio.start_background_task(pidWrapper, kid=kid)


def pidWrapper(kid):
    k = Kettle.query.get(kid)
    config =  json.loads(k.automatic)
    config_obj = {}
    for c in config["parameter"]:
        config_obj[c["name"]] = c["value"]

    for i in app.brewapp_pid:
        if(i.__name__ == config["name"]):
            p  = i(kid)
            p.config = config_obj
            p.run()
            break
