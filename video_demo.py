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

RST = 24
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()
disp.clear()
disp.display()
font = ImageFont.load_default()


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
    global delay,alert,adj_delay,adj_button
    try:
		json_data = json.loads(str(msg.payload))
		print "json_data: "+str(json_data)
		if json_data['type'] == 'control':
			delay = json_data['value']
			print 'Now! Delay is '+str(delay)
		elif json_data['type'] == 'alert':
			alert = 1
			adj_delay = json_data['value']
		elif json_data['type'] == 'adjusting':
			adj_button = 1
    except ValueError:
		print 'parse wrong!'
		#return

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

global delay,loop,alert,adj_delay,adj_button
delay = 0.004
loop = 1
alert = 0
adj_delay = 1
adj_button = 0

def oled_display():
	global delay,loop,alert,adj_delay,adj_button
	image = Image.open('boot.ppm').convert('1')
	draw = ImageDraw.Draw(image)
	draw.text((13,50), 'Windows Starting.', font=font, fill=255)
	disp.image(image)
	disp.display()
	time.sleep(1)
	image = Image.open('boot.ppm').convert('1')
	draw = ImageDraw.Draw(image)
	draw.text((13,50), 'Windows Starting..', font=font, fill=255)
	disp.image(image)
	disp.display()
	time.sleep(1)
	image = Image.open('boot.ppm').convert('1')
	draw = ImageDraw.Draw(image)
	draw.text((13,50), 'Windows Starting...', font=font, fill=255)
	disp.image(image)
	disp.display()
	time.sleep(1)

	while loop:
		if alert == 1:
			led_off(LED_1)
			led_off(LED_2)
			led_on(LED_3)
			#image = Image.new('1',(128,64))
			image = Image.open('alert.ppm').convert('1')
			draw = ImageDraw.Draw(image)
			disp.image(image)
			disp.display()
			if adj_button == 1:
				image = Image.open('adjusting.ppm').convert('1')
				draw = ImageDraw.Draw(image)
				disp.image(image)
				disp.display()
				time.sleep(3)
				delay = adj_delay
				alert = 0
				adj_button = 0
		else:
			led_off(LED_1)
			led_off(LED_3)
			led_on(LED_2)
			#image = Image.new('1',(128,64))
			image = Image.open('bk.ppm').convert('1')
			draw = ImageDraw.Draw(image)
			draw.text((0,20), 'Conveyor:', font=font, fill=255)
			draw.text((0,40), 'Mixer:   ', font=font, fill=255)
			draw.text((70,20), '%.2f'%(1.0/delay+random.uniform(-5,5)), font=font, fill=255)
			draw.text((70,40), '%.2f'%(1.0/delay+random.uniform(-5,5)), font=font, fill=255)
			draw.text((110,20), 'm^3', font=font, fill=255)
			draw.text((110,40), 'm^3', font=font, fill=255)
			draw.line((0,35,127,35), fill=255)
			disp.image(image)
			disp.display()
			time.sleep(1)

#start motor_run thread
t = threading.Thread(target=motor_run)
t.start()
t1 = threading.Thread(target=oled_display)
t1.start()

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
