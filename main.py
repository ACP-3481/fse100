#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from playsound import playsound
from hx711 import HX711

TRIG = 11 #ultrasonic input GPIO 17
ECHO = 12 #ultrasonic output GPIO 18
VIBRATION_PIN = 18 # GPIO 24
# distance thresholds (cm)
FULL_DISTANCE = 24
HALF_DISTANCE = 26
TRIG2 = 29 # ultrasonic (proximity) input GPIO 5
ECHO2 = 31 # ultrasonic (proximity) output GPIO 6

# weight sensor pins
DOUT = 33 # GPIO 13
PD_SCK = 35 # GPIO 19
REFERENCE_UNIT = 678
GAIN = 1
HALF_WEIGHT = 60
FULL_WEIGHT = 110

PROXIMITY_THRESHOLD = 6.5 # cm

def setup() -> None:
    """
    Setup for GPIO pins in BOARD mode
    """
    GPIO.setmode(GPIO.BOARD)
    # ultrasonic setup
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN) # read from ultrasonic

    # proximity setup
    GPIO.setup(TRIG2, GPIO.OUT)
    GPIO.setup(ECHO2, GPIO.IN)

    # Set Vibration motor pin
    GPIO.setup(VIBRATION_PIN, GPIO.OUT)
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

    # initialize weight sensor
    global hx
    hx = HX711(DOUT, PD_SCK)
    hx.set_reading_format("MSB", "MSB")

    hx.set_reference_unit(REFERENCE_UNIT)
    hx.reset()


def vibrate_on():
    GPIO.output(VIBRATION_PIN, GPIO.HIGH)

def vibrate_off():
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

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
    return during * 340 / 2 * 100 # Speed of sound = 340 m/s, convert to cm

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

def loop():
    """
    Main program loop.
    """
    # flags to prevent the speaker from looping
    currentlyOn = False
    currentlyOff = False
    currentlyFull = False
    currentlyHalf = False
    while True:
        currProximity = proximity()
        print(f"Proximity: {currProximity}")
        # start when the cup is within the proximity threshold
        if currProximity <= PROXIMITY_THRESHOLD:
            if not currentlyOn:
            # only run on state change to On
                print("Playing on.mp3")
                playsound("assets/on.mp3")
                currentlyOn = True
                currentlyOff = False
                time.sleep(1)
                hx.tare()
            dis = distance()
            print(dis, 'cm')
            print()
            weight = hx.get_weight(5)
            # Monitor for weight and distance thresholds
            if weight >= FULL_WEIGHT and dis <= FULL_DISTANCE:
                vibrate_on() # vibrates on full
                if not currentlyFull:
                # only run on state change to Full
                    currentlyFull = True
                    currentlyHalf = False
                    print("Playing full.mp3")
                    playsound("assets/full.mp3")
            elif weight >= HALF_WEIGHT and dis <= HALF_DISTANCE:
                vibrate_off()
                if not currentlyHalf:
                # only run on state change to Half
                    currentlyHalf = True
                    currentlyFull = False
                    print("Playing half.mp3")
                    playsound("assets/half.mp3")
            else:
                # reset state if no thresholds are met
                currentlyHalf = False
                currentlyFull = False
                vibrate_off()
            time.sleep(0.3)
        else:
            if not currentlyOff:
            # only run on state change to Off
                print("Playing off.mp3")
                playsound("assets/off.mp3")
                currentlyOff = True
                currentlyOn = False

def destroy():
    """
    Deprograms pins for safe exit
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
        print(exc)
        destroy()

