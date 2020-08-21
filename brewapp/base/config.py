from flask import json

import yaml

from .. import app, db, manager, socketio
from .devices import (chip_gpio, dummygpio, gembird, gpio, gpiosys,
                                  piface, wifisocket)
from .model import Config
from .thermometer import (dummy_thermometer, usb_thermometer,
                                      w1_thermometer, w1_thermometer2)
from .util import brewinit


def pre_post(data, **kw):
    if data["type"] == "json":
        data["value"] = json.dumps(data["value"])


def post_post(result, **kw):
    if result["type"] == "json":
        result["value"] = json.loads(result["value"])
    readConfig()
    socketio.emit('config', app.brewapp_config, namespace='/brew')


def post_get_many(result, **kw):
    for o in result["objects"]:
        if o["type"] == "json":
            o["value"] = json.loads(o["value"])

    result["objects"] = sorted(result["objects"], key=lambda k: k['name'])


def readConfig():
    app.brewapp_config = {}
    config = Config.query.all()
    for c in config:
        app.brewapp_config[c.name] = c.value


@brewinit(-1001)
def initConfig():
    if (app.createdb is False):
        return

    with open("config/config.yaml", 'r') as stream:
        try:
            y = yaml.load(stream)
            for k in y.keys():
                opts = y[k].get("options", None)
                if opts is not None:
                    opts = ",".join(opts)

                db.session.add(
                    Config(
                        name=k,
                        value=y[k].get("value", None),
                        type=y[k].get("type", None),
                        description=y[k].get("description", None),
                        options=opts
                    )
                )
            db.session.commit()
        except yaml.YAMLError as exc:
            app.logger.error(f"Load config ERROR {exc}")


@brewinit(order=-1000)
def init():
    manager.create_api(
        Config,
        methods=['GET', 'POST', 'DELETE', 'PUT'],
        preprocessors={
            'POST':[pre_post],
            'PATCH_SINGLE': [pre_post]
        },
        postprocessors={
            'POST':[post_post],
            'GET_MANY': [post_get_many],
            'GET_SINGLE':[post_post],
            'PATCH_SINGLE': [post_post]
        }
    )
    readConfig()


@app.route('/api/config/setup', methods=['GET'])
def config_setup():
    return json.dumps({"setup": app.brewapp_config.get("SETUP", "NO")})


@brewinit()
def initDriver():
    app.logger.info("INIT Driver")

    hardware= {
        'DUMMY': dummygpio.DummyGPIO(),
        'GPIO': gpio.BrewGPIO(),
        'GEMBIRD': gembird.GembirdUSB(),
        'PIFACE': piface.PiFace(),
        'WIFISOCKET': wifisocket.WifiSocket(),
        'CHIP-GPIO': chip_gpio.BrewGPIO(),
        'GPIOSYS': gpiosys.GPIOSys()
    }

    thermometer = {
        'DUMMY': dummy_thermometer.DummyThermometer(),
        '1WIRE': w1_thermometer.OneWireThermometer(),
        '1WIRE_V2': w1_thermometer2.OneWireThermometer2(),
        'USB': usb_thermometer.USBThermometer()
    }

    app.brewapp_hardware = hardware.get(
        app.brewapp_config.get("SWITCH_TYPE", "DUMMY"),
        dummygpio.DummyGPIO()
    )
    app.brewapp_thermometer = thermometer.get(
        app.brewapp_config.get("THERMOMETER_TYPE", "DUMMY"),
        dummy_thermometer.DummyThermometer()
    )
    app.logger.info(app.brewapp_hardware)
    app.logger.info(app.brewapp_thermometer)
