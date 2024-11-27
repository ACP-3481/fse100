import traceback
import RPi.GPIO as GPIO
import time

VIBRATION_PIN = 18 # GPIO 24


def setup():
    # Set Vibration motor pin
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(VIBRATION_PIN, GPIO.OUT)
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

def vibrate_on():
    GPIO.output(VIBRATION_PIN, GPIO.HIGH)

def vibrate_off():
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

def loop():
    vibrate_on()
    time.sleep(1)
    vibrate_off()
    time.sleep(1)


def destroy():
    """
    Deprograms the pins for safe exit
    """
    # turn off vibration motor
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt as exc:
        print(exc)
        destroy()
    except Exception as exc:
        traceback.print_exc()
        destroy()
