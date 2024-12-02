import RPi.GPIO as GPIO
import time
from playsound import playsound
import threading
from hx711 import HX711

TRIG = 11  # ultrasonic input GPIO 17
ECHO = 12  # ultrasonic output GPIO 18
VIBRATION_PIN = 18  # GPIO 24
FULL_DISTANCE = 5
HALF_DISTANCE = 10

# weight sensor pins
DOUT = 33 # GPIO 13
PD_SCK = 35 # GPIO 19
REFERENCE_UNIT = 678
GAIN = 1 # FIXME figure out gain
HALF_WEIGHT = 60
FULL_WEIGHT = 110

def setup() -> None:
    """
    Setup for GPIO pins in BOARD mode
    """
    GPIO.setmode(GPIO.BOARD)
    # ultrasonic setup
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)  # read from ultrasonic

    # Set Vibration motor pin
    GPIO.setup(VIBRATION_PIN, GPIO.OUT)
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

    # initialize weight sensor
    global hx
    hx = HX711(DOUT, PD_SCK)
    hx.set_reading_format("MSB", "MSB") # FIXME figure out if it should be MSB or LSB

    hx.set_reference_unit(REFERENCE_UNIT)
    hx.reset()


def vibrate_on():
    GPIO.output(VIBRATION_PIN, GPIO.HIGH)

def vibrate_off():
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

def map_value(x, in_min, in_max, out_min, out_max):
    """
    Converts an input value x from one range into another range
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def distance() -> float:
    """
    Gets the distance from the ultrasonic sensor in cm
    """
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)  # wait 2 microseconds to ensure the pin settles

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)  # wait 10 microseconds to trigger the ultrasonic pulse
    GPIO.output(TRIG, 0)

    timeout = time.time() + 0.02  # 20 ms timeout
    while GPIO.input(ECHO) == 0:  # wait for ECHO to go high
        if time.time() > timeout:
            print("Timeout waiting for ECHO to go high")
            return -1
    time1 = time.time()
    timeout = time.time() + 0.02  # another 20 ms timeout
    while GPIO.input(ECHO) == 1:  # wait for ECHO to go low
        if time.time() > timeout:
            print("Timeout waiting for ECHO to go low")
            return -1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100  # Speed of sound = 340 m/s, convert to cm

def loop():
    """
    Main program loop.
    """
    currentlyFull = False
    currentlyHalf = False
    while True:
        print("here 2")
        currProximity = proximity()
        print(f"Proximity: {currProximity}")
        if currProximity <= 6.5: # only run when cup is within 5 cm
            if not currentlyOn:
                print("Playing on.mp3")
                playsound("on.mp3")
                currentlyOn = True
                currentlyOff = False
                time.sleep(1)
                hx.tare()
            dis = distance()
            print(dis, 'cm')
            print()
            weight = hx.get_weight(5)
            if weight >= FULL_WEIGHT: # and dis <= FULL_DISTANCE:
                vibrate_on()
                if not currentlyFull:
                    currentlyFull = True
                    currentlyHalf = False
                    print("Playing full.mp3")
                    playsound("full.mp3")
            elif weight >= HALF_WEIGHT: # and dis <= HALF_DISTANCE:
                vibrate_off()
                if not currentlyHalf:
                    currentlyHalf = True
                    currentlyFull = False
                    print("Playing half.mp3")
                    playsound("half.mp3")
            else:
                currentlyHalf = False
                print("Playing full.mp3")
                playsound("full.mp3")
        elif dis <= HALF_DISTANCE:
            vibrate_off()
            if not currentlyHalf:
                currentlyHalf = True
                currentlyFull = False
                print("Playing half.mp3")
                playsound("half.mp3")
        else:
            currentlyHalf = False
            currentlyFull = False
            vibrate_off()
        time.sleep(0.3)

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
        import traceback
        traceback.print_exc()
        destroy()

