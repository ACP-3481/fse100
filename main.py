#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

colors = (0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF)
colors_dict = {
    "Red": 0xFF0000,
    "Green": 0x00FF00,
    "Blue": 0x0000FF,
    "Yellow": 0xFFFF00,
    "Magenta": 0xFF00FF,
    "Cyan": 0x00FFFF,
    "Off": 0x000000
}
TRIG = 11 #ultrasonic input GPIO 17
ECHO = 12 #ultrasonic output GPIO 18
R = 13 # LED red pin GPIO 27
G = 15 # LED green pin GPIO 22
VIBRATION_PIN = 18 # GPIO 24
FULL_DISTANCE = 5
HALF_DISTANCE = 10

def setup() -> None:
    """
    Setup for GPIO pins in BOARD mode
    """
    global p_R
    global p_G
    GPIO.setmode(GPIO.BOARD)
    # ultrasonic setup
    GPIO.setup(TRIG, GPIO.OUT) 
    GPIO.setup(ECHO, GPIO.IN) # read from ultrasonic

    # dual color LED setup
    GPIO.setup(R, GPIO.OUT)
    GPIO.setup(G, GPIO.OUT)

    # set LED pins to LOW / off
    GPIO.output(R, GPIO.LOW)
    GPIO.output(G, GPIO.LOW)

    p_R = GPIO.PWM(R, 2000) # set frequency to 2KHz
    p_G = GPIO.PWM(G, 2000)

    # Initial duty Cycle = 0 (leds off)
    p_R.start(0)
    p_G.start(0)

    # Set Vibration motor pin
    GPIO.setup(VIBRATION_PIN, GPIO.OUT)
    GPIO.output(VIBRATION_PIN, GPIO.LOW)

def vibrate_on():
    GPIO.output(VIBRATION_PIN, GPIO.HIGH)

def vibrate_off():
    GPIO.output(VIBRATION_PIN, GPIO.LOW)


def map(x, in_min, in_max, out_min, out_max):
    """
    Converts an input value x from one range into another range
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col: int) -> None:
    """
    Sets the led to a color based on a 24-bit int
    """
    # get individual rgb values from 24-bit color
    R_val = col >> 16
    G_val = (col >> 8) & 0x00FF

    # map the rgb values (0-255) into rpi duty cycles (0-100%)
    R_val = map(R_val, 0, 255, 0, 100)
    G_val = map(G_val, 0, 255, 0, 100)

    p_R.ChangeDutyCycle(R_val)
    p_G.ChangeDutyCycle(G_val)

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

def loop():
    """
    Main program loop.
    """
    while True:
        dis = distance()
        print(dis, 'cm')
        print()
        if dis <= FULL_DISTANCE:
            setColor(colors_dict["Red"])
            vibrate_on()
        elif dis <= HALF_DISTANCE:
            setColor(colors_dict["Yellow"])
            vibrate_off()
        else:
            setColor(colors_dict["Off"])
            vibrate_off()
        time.sleep(0.3)

def destroy():
    """
    Deprograms the pins for safe exit
    """
    # turn off leds
    p_R.stop()
    p_G.stop()
    GPIO.output(R, GPIO.LOW)
    GPIO.output(G, GPIO.LOW)

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
