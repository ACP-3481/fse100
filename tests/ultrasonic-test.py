import traceback
import RPi.GPIO as GPIO
import time

TRIG = 11 #ultrasonic input GPIO 17
ECHO = 12 #ultrasonic output GPIO 18

def setup():
    GPIO.setmode(GPIO.BOARD)
    # ultrasonic setup
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

def loop():
    dis = distance()
    print(f"{dis} cm")


def destroy():
    """
    Deprograms the pins for safe exit
    """
    GPIO.cleanup()

def distance() -> float:
    """
    Gets the distance from the ultrasonic sensor in cm
    """
    GPIO.output(TRIG, 0)
    time.sleep(0.000002) # wait 2 microseconds to ensure the pin settles

    GPIO.output(TRIG, 1)
    time.sleep(0.00001) # wait 10 microseconds to trigger the ultrasonic pulse
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0: # wait for ECHO to go high
        pass
    time1 = time.time()
    while GPIO.input(ECHO) == 1: # wait for ECHO to go low
        pass
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

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