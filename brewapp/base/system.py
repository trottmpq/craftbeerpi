import threading
import time
from subprocess import call

from brewapp import app
from brewapp.base.views import base

# from _thread import start_new_thread
## Restart Endpoint
@app.route('/restart')
def restart():
    app.logger.info("--> RESTART TRIGGERED")
    ## Do in other thread
    threading.Thread(target=doRestart).start()
    # start_new_thread(doRestart,())
    return base.send_static_file("restart.html")

## Execute Restart
def doRestart():
    time.sleep(5)
    app.logger.info("--> RESTART EXECUTE")
    call(["/etc/init.d/craftbeerpiboot", "restart"])


## Shutdown Endpoint
@app.route('/halt')
def halt():
    app.logger.info("--> HALT TRIGGERED")
    ## Do in other thread
    threading.Thread(target=doHalt).start()
    # start_new_thread(doHalt,())
    return app.send_static_file("halt.html")


# Execute Restart
def doHalt():
    time.sleep(5)
    app.logger.info("--> HALT EXECUTE")
    call("halt")
