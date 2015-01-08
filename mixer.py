#!/usr/bin/env python
#change concrete plant step motors speed through subscribing mqtt topic "motor_geer"
#diplay motor speed on OLED 128*64
#By Haotian Wang @Dec,2014

import time
import mosquitto
import json
import os
import RPi.GPIO as GPIO
import threading
import Adafruit_SSD1306
import Image
import ImageDraw
import ImageFont
import random


#GPIO intitialization
GPIO.setmode (GPIO.BCM)
GPIO.setup(9,GPIO.OUT)
p = GPIO.PWM(9,1000)
p.start(0)
#callback function for mqtt
def on_message(mosq, userdata, msg):
    global delay,alert,adj_delay,adj_button
    try:
		speed = str(msg.payload)
		print 'speed is:'+speed
		p.ChangeDutyCycle(int(speed))
    except ValueError:
		print 'parse wrong!'

#mqtt initializaiton
mqtt_client = mosquitto.Mosquitto('mixer')
mqtt_client.on_message = on_message
mqtt_client.connect('127.0.0.1')
mqtt_client.subscribe('mixer_motor')

loop = 1
while loop :
    try:
		ret = mqtt_client.loop()
		if ret == 0:
			print 'mqtt listening!'
		else:
			mqtt_client.unsubscribe('mixer')#motor_geer
			mqtt_client.disconnect()
			mqtt_client.connect('127.0.0.1')
			mqtt_client.subscribe('mixer')
    except KeyboardInterrupt:
		print 'BYE!'
		loop = 0
