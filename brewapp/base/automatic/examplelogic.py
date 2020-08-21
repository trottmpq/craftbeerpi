import time

from ... import app, socketio
from ..util import *
from .automaticlogic import *


@brewautomatic()
class CustomLogic(Automatic):

    # Define config paramter as array of dicts
    configparameter = [{"name" : "PumpGPIO" , "value" : 17}]

    def run(self):
        # loop for automatic
        while self.isRunning():
            # access config paramter at runtime


            # make sure to add a sleep to the while loop
            socketio.sleep(1)
