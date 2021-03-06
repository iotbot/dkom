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
    global delay
    try:
		json_data = json.loads(str(msg.payload))
		print "json_data: "+str(json_data)
		delay = json_data['mode']
		print 'Now! Delay is '+str(delay)

		#image = Image.new('1',(128,64))
		#draw = ImageDraw.Draw(image)
		#draw.text((0,20), 'Conveyor:', font=font, fill=255)
		#draw.text((0,40), 'Mixer:   ', font=font, fill=255)
		#draw.text((70,20), '%.2f'%(1.0/delay), font=font, fill=255)
		#draw.text((70,40), '%.2f'%(1.0/delay), font=font, fill=255)
		#draw.text((110,20), 'm^3', font=font, fill=255)
		#draw.text((110,40), 'm^3', font=font, fill=255)
		#draw.line((0,35,127,35), fill=255)
		#disp.image(image)
		#disp.display()

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

def oled_display():
	global delay,loop
	while loop:
		image = Image.new('1',(128,64))
		draw = ImageDraw.Draw(image)
		draw.text((0,20), 'Conveyor:', font=font, fill=255)
		draw.text((0,40), 'Mixer:   ', font=font, fill=255)
		draw.text((70,20), '%.2f'%(1.0/delay), font=font, fill=255)
		draw.text((70,40), '%.2f'%(1.0/delay), font=font, fill=255)
		draw.text((110,20), 'm^3', font=font, fill=255)
		draw.text((110,40), 'm^3', font=font, fill=255)
		draw.line((0,35,127,35), fill=255)
		disp.image(image)
		disp.display()

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
