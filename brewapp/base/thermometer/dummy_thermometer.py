import json
import os
import re
from decimal import ROUND_HALF_UP, Decimal
from random import randint, uniform
from subprocess import PIPE, Popen, call

from flask import Blueprint, json, render_template, request

from ... import app, socketio
from ..model import *

app.cbp["TEMP"] = {"DummySensor1": 20.99, "DummySensor2": 20, "DummySensor3": 20}

class DummyThermometer(object):

    def init(self):
        print ("INIT")

    def getSensors(self):
        return ["DummySensor1","DummySensor2","DummySensor3"]

    def readTemp(self, tempSensorId):
        try:
            return app.cbp["TEMP"][tempSensorId]
        except Exception as e:
            print(e)
            return None
            
@app.route('/api/test/temps', methods=['GET'])
def dummy_temps():
    return json.dumps(app.cbp["TEMP"])

@app.route('/set', methods=["POST"])
def test_set():
    dataDict = json.loads(request.data)
    print(app.cbp)
    app.cbp["TEMP"][dataDict["id"]] = dataDict.get("value", None)
    return ('', 204)
