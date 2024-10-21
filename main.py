#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

colors = (0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF)
TRIG = 11 #ultrasonic input
ECHO = 12 #ultrasonic output
R = 11 # LED red pin
G = 12 # LED green pin
FULL_DISTANCE = 5

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

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):
    R_val = col >> 8
    G_val = col & 0x00FF

    R_val = map(R_val, 0, 255, 0, 100)
    G_val = map(G_val, 0, 255, 0, 100)

    p_R.ChangeDutyCycle(R_val)
    p_G.ChangeDutyCycle(G_val)

def distance() -> float:
    """
    Gets the distance from the ultrasonic sensor in cm
    """
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(ECHO) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def loop():
    """
    Main program loop.
    """
    while True:
        dis = distance()
        print(dis, 'cm')
        print()
        if dis <= FULL_DISTANCE:
            setColor(colors[0])
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
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except Exception as exc:
        print(exc)
        destroy()
