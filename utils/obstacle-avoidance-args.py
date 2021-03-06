#!/usr/bin/python
import time
import RPi.GPIO as GPIO
import argparse
#Ability to read arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d","--distance",help="Add the set distance (def. 50cm)")
args = parser.parse_args()

#Setting the GPIO library to use the BCM layout
GPIO.setmode(GPIO.BCM)
print("Program started")

#Ultrasonic sensor pins
TRIGGER_LEFT = 4
ECHO_LEFT = 17
TRIGGER_RIGHT = 27
ECHO_RIGHT = 22
TRIGGER_CENTER = 23
ECHO_CENTER = 24
#Motor pins
MOTOR_A1 = 5
MOTOR_A2 = 6
MOTOR_B1 = 13
MOTOR_B2 = 26
#Preset dist
dist_left = 0
dist_right = 0
dist_center = 0

#Checking for an argument
if args.distance:
    avoid_at = int(args.distance) #cm
else:
    avoid_at = 50 #cm (default)

#How long the rover turns    
turn_time = 0.5 #seconds

print("Pin def succes")

#Setting up the GPIO pins
GPIO.setup(TRIGGER_LEFT,GPIO.OUT)
GPIO.setup(ECHO_LEFT,GPIO.IN)      

GPIO.setup(TRIGGER_RIGHT,GPIO.OUT)
GPIO.setup(ECHO_RIGHT,GPIO.IN)

GPIO.setup(TRIGGER_CENTER, GPIO.OUT)
GPIO.setup(ECHO_CENTER, GPIO.IN)

GPIO.setup(MOTOR_A1, GPIO.OUT)
GPIO.setup(MOTOR_A2, GPIO.OUT)
GPIO.setup(MOTOR_B1, GPIO.OUT)
GPIO.setup(MOTOR_B2, GPIO.OUT)
print("Pin setup success")

#####################################
#####################################

#function for retrieving the distance
def getdist(trigger, echo):
    #Sending the 10microsecond pulse nedded
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)
    #When echo goes high the time starts
    while GPIO.input(echo)==0:
        pass
    start = time.time()
    #When echo goes low the time stops
    while GPIO.input(echo)==1:
        pass
    stop = time.time()

    #The time difference * speedofsound
    #Divided by two since the since the distance meassured is back and forth
    distance = ((stop-start) * 34000)/2

    return distance

#The functions for the movement
def forward():
    GPIO.output(MOTOR_A1, True)
    GPIO.output(MOTOR_A2, False)
    GPIO.output(MOTOR_B1, True)
    GPIO.output(MOTOR_B2, False)
    print("Forward.")
    return


def left():
    GPIO.output(MOTOR_A1, False)
    GPIO.output(MOTOR_A2, True)
    GPIO.output(MOTOR_B1, True)
    GPIO.output(MOTOR_B2, False)
    print("Turning left.")
    return

def right():
    GPIO.output(MOTOR_A1, True)
    GPIO.output(MOTOR_A2, False)
    GPIO.output(MOTOR_B1, False)
    GPIO.output(MOTOR_B2, True)
    print("Turning right.")
    return

def stop():
    GPIO.output(MOTOR_A1, False)
    GPIO.output(MOTOR_A2, False)
    GPIO.output(MOTOR_B1, False)
    GPIO.output(MOTOR_B2, False)
    print("Stopping.")
    return

def reverse():
    GPIO.output(MOTOR_A1, False)
    GPIO.output(MOTOR_A2, True)
    GPIO.output(MOTOR_B1, False)
    GPIO.output(MOTOR_B2, True)
    print("Reversing")    
    return

#####################################
#####################################

#Setting up the sensor (0.1second to 'load' the module)
GPIO.output(TRIGGER_LEFT, False)
GPIO.output(TRIGGER_RIGHT, False)
time.sleep(0.1)

#Getting an inital distance
dist_left = getdist(TRIGGER_LEFT, ECHO_LEFT)
time.sleep(0.1)
dist_right = getdist(TRIGGER_RIGHT, ECHO_RIGHT)
time.sleep(0.1)
dist_center = getdist(TRIGGER_CENTER, ECHO_CENTER)
time.sleep(0.1)

print("Inital distance complete")
try:
    print("Navigation loop started")
    while True:
        #The time between each cycle (mininum recommended is 60ms)
        time.sleep(0.200)
        #Measuring the distances
        dist_left = getdist(TRIGGER_LEFT, ECHO_LEFT)
        dist_right = getdist(TRIGGER_RIGHT, ECHO_RIGHT)
        dist_center = getdist(TRIGGER_CENTER, ECHO_CENTER)
        #Moves forward (As a default)
        forward()
        print("Going forward")

        #Checking the different thresholds
        if dist_left < avoid_at:
            right()
            print("dist_left ("+str(dist_left)+") < " + str(avoid_at) + " -> Turning right")
            time.sleep(turn_time)
        elif dist_right < avoid_at:
            left()
            print("dist_right ("+str(dist_right)+") < " + str(avoid_at) + " -> Turning left")
            time.sleep(turn_time)
        elif dist_center < avoid_at:
            print("dist_center (" + str(dist_center)+ ") < " + str(avoid_at) + " --> Detecting optimal direction")
            if dist_left < dist_right:
                print("dist_left < dist_right -> Turning right")
                right()
                time.sleep(turn_time)
            else:
                print("dist_left > dist_right -> Turning left")
                left()
                time.sleep(turn_time)

except KeyboardInterrupt:
    #The code waits for a keyboardinterrupt
    #Which ends the while loop
    pass

#Cleans up the GPIO pins, to safely exit the code.
GPIO.cleanup()
