#!/usr/bin/env python
#change concrete plant step motors speed through subscribing mqtt topic "motor_geer"
#diplay motor speed on OLED 128*64
#add temperature and pressure monitoring
#By Haotian Wang @Dec,2014

import time
import mosquitto
import os
import random
mqtt_client = mosquitto.Mosquitto('websock_test')
mqtt_client.connect('127.0.0.1')
while 1:
	data = 200 + random.uniform(-10,10)
	print data
	json_data = '{"dev_t":"sensor","dev_id":"pump_motor_speed","data_t":"num","value":'+str(data)+',"timestamp":'+str(time.time())+'}'
	mqtt_client.publish('test',json_data)
	time.sleep(1)
