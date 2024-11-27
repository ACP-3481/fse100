import traceback
import RPi.GPIO as GPIO
import time

TRIG2 = 29 # ultrasonic (proximity) input GPIO 5
ECHO2 = 31 # ultrasonic (proximity) output GPIO 6

def proximity() -> float:
    """
    Gets the distance from the proximity sensor in cm
    """
    GPIO.output(TRIG2, 0)
    time.sleep(0.000002) # wait 2 microseconds to ensure the pin settles

    GPIO.output(TRIG2, 1)
    time.sleep(0.00001) # wait 10 microseconds to trigger the ultrasonic pulse
    GPIO.output(TRIG2, 0)

    while GPIO.input(ECHO2) == 0: # wait for ECHO to go high
        pass
    time1 = time.time()
    while GPIO.input(ECHO2) == 1: # wait for ECHO to go low
        pass
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100 # Speed of sound = 340 m/s, convert to cm

def setup():
    # proximity setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG2, GPIO.OUT)
    GPIO.setup(ECHO2, GPIO.IN)

def loop():
    prox = proximity()
    print(f"{prox} cm")


def destroy():
    """
    Deprograms the pins for safe exit
    """
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
