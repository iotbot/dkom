#!/usr/bin/env python
#change concrete plant step motors speed through subscribing mqtt topic "motor_geer"
#By Haotian Wang @Dec,2014

import time
import mosquitto
import json
import os
import RPi.GPIO as GPIO
import threading

#GPIO intitialization
GPIO.setmode (GPIO.BCM)
A_coil_A_1_pin = 17
A_coil_A_2_pin = 18
A_coil_B_1_pin = 22
A_coil_B_2_pin = 23
GPIO.setup(A_coil_A_1_pin,GPIO.OUT)
GPIO.setup(A_coil_A_2_pin,GPIO.OUT)
GPIO.setup(A_coil_B_1_pin,GPIO.OUT)
GPIO.setup(A_coil_B_2_pin,GPIO.OUT)
B_coil_A_1_pin = 9
B_coil_A_2_pin = 25
B_coil_B_1_pin = 11
B_coil_B_2_pin = 8
GPIO.setup(B_coil_A_1_pin,GPIO.OUT)
GPIO.setup(B_coil_A_2_pin,GPIO.OUT)
GPIO.setup(B_coil_B_1_pin,GPIO.OUT)
GPIO.setup(B_coil_B_2_pin,GPIO.OUT)
LED_1 = 5
LED_2 = 6
LED_3 = 12
GPIO.setup(LED_1,GPIO.OUT)
GPIO.setup(LED_2,GPIO.OUT)
GPIO.setup(LED_3,GPIO.OUT)

def led_off(pin):
	GPIO.output(pin,True)

def led_on(pin):
	GPIO.output(pin,False)

def setStep(w1,w2,w3,w4):
   GPIO.output(A_coil_A_1_pin,w1)
   GPIO.output(A_coil_A_2_pin,w2)
   GPIO.output(A_coil_B_1_pin,w3)
   GPIO.output(A_coil_B_2_pin,w4)
   GPIO.output(B_coil_A_1_pin,w1)
   GPIO.output(B_coil_A_2_pin,w2)
   GPIO.output(B_coil_B_1_pin,w3)
   GPIO.output(B_coil_B_2_pin,w4)


#callback function for mqtt
def on_message(mosq, userdata, msg):
    global delay
    try:
		json_data = json.loads(str(msg.payload))
		print "json_data: "+str(json_data)
		delay = json_data['mode']
		print 'Now! Delay is '+str(delay)
		if delay <= 0.01:
			led_off(LED_2)
			led_off(LED_3)
			led_on(LED_1)
		elif delay <= 0.022:
			led_off(LED_1)
			led_off(LED_3)
			led_on(LED_2)
		else:
			led_off(LED_1)
			led_off(LED_2)
			led_on(LED_3)
    except ValueError:
		print 'parse wrong!'
		return

#mqtt initializaiton
mqtt_client = mosquitto.Mosquitto('motor1')
mqtt_client.on_message = on_message
mqtt_client.connect('127.0.0.1')
mqtt_client.subscribe('pump')

#motor run thread
def motor_run():
	global delay,loop
	while loop:
		setStep(1,0,1,0)
		time.sleep(delay)
		setStep(0,1,1,0)
		time.sleep(delay)
		setStep(0,1,0,1)
		time.sleep(delay)
		setStep(1,0,0,1)
		time.sleep(delay)
global delay,loop
delay = 0.004
loop = 1

#start motor_run thread
t = threading.Thread(target=motor_run)
t.start()

while loop :
    try:
		ret = mqtt_client.loop()
		if ret == 0:
			print 'mqtt listening!'
		else:
			mqtt_client.unsubscribe('pump')#motor_geer
			mqtt_client.disconnect()
			mqtt_client.connect('127.0.0.1')
			mqtt_client.subscribe('pump')
    except KeyboardInterrupt:
		print 'BYE!'
		loop = 0
