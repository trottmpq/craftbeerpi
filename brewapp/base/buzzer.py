# from _thread import start_new_thread
import threading
import time

from .. import app
from .util import brewinit

try:
    import RPi.GPIO as GPIO
    app.logger.info("SETUP GPIO Module for Buzzer")
except Exception as e:
    app.logger.error(f"SETUP GPIO Module for Buzzer Failed: {e}")
    pass


@brewinit()
def initBuzzer():
    buzzer_gpio = app.brewapp_config.get("BUZZER_GPIO", None)
    app.logger.info(f"BUZZER GPIO: {buzzer_gpio}")
    try:
        if buzzer_gpio:
            buzzer_gpio = int(buzzer_gpio)
        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(buzzer_gpio, GPIO.IN)
        GPIO.setup(buzzer_gpio, GPIO.OUT)

    except Exception as e:
        app.logger.error(e)

## melody Pattern
## H = HIGH
## L = LOW
## Float value as pause
## it must be a L at the end to turn the sound off
def nextStepBeep():
    sound1 = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]
    threading.Thread(target=playSound, args=(sound1)).start()
    # start_new_thread(playSound,(sound1,))


def timerBeep():
    sound2 = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]
    threading.Thread(target=playSound, args=(sound2)).start()
    # start_new_thread(playSound,(sound2,))


def resetBeep():
    sound3 = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]
    threading.Thread(target=playSound, args=(sound3)).start()
    # start_new_thread(playSound,(sound3,))


# Logic to play the sound melody
def playSound(melody):
    buzzer_gpio = app.brewapp_config.get("BUZZER_GPIO", None)
    if buzzer_gpio:
        for i in melody:
            if(isinstance(i, str)):
                if i == "H":
                    GPIO.output(int(buzzer_gpio), GPIO.HIGH)
                else:
                    GPIO.output(int(buzzer_gpio), GPIO.LOW)
            else:
                time.sleep(i)
