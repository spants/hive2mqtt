"""

hive2mqtt.py 
------------
Version 1.1
v1.0 - initial release
v1.1 - Try to take into account non active 2 users 

Note: requires a config file as hsown below.

Reads key information from Hive Active 2 and publishes it on a MQTT server for use with Home Automation,
NodeRed and other systems such as EMONCMS and Domoticz. With mqtt, the world is open to you.
Feel free to copy/change (following the GPLv3 licence below) but please include a reference to my blog:
http://blog.spants.com @spantsUK
------------
based on hive2oem.py

Reads data from Hive
Sends data to emoncms

Based on MiHive (c) 2014 David Tarrant
License: GPLv3

also see http://britishgashive.freeforums.org/automated-json-feed-retrieval-t7-20.html
"""

import cookielib
import urllib
import urllib2
import json
from csv import DictWriter
import os
import time
from datetime import date

import paho.mqtt.client as paho

mqttc = paho.Client()


def mqttsend( topic, data, retain ):
   
   qos=0
   topic = mqtttopic + topic

   if (data is not None) and (data is not "--"):
   		mqttc.publish(topic, data, qos, retain);
   		print topic, data, retain
   return;


# Open config file
json_data=open('/home/pi/hive_config.json')

config = json.load(json_data)
json_data.close()

config = config["config"]
username = config[0]["username"]
password = config[1]["password"]
mqtthost = config[2]["mqtthost"]
mqttport = int(float(config[3]["mqttport"]))
mqttuser = config[4]["mqttuser"]
mqttpass = config[5]["mqttpass"]
mqtttopic = config[6]["mqtttopic"]

mqttc.username_pw_set(mqttuser, mqttpass)
mqttc.connect(mqtthost, mqttport, 60, bind_address="")

def makeRequest(url,payload):
   global urllib2
   global opener
   if payload:
	# Use urllib to encode the payload
	data = urllib.urlencode(payload)
	# Build our Request object (supplying 'data' makes it a POST)
	req = urllib2.Request(url, data)
   else:
	req = urllib2.Request(url)

   # Make the request and read the response
   try:
	resp = urllib2.urlopen(req)
   except urllib2.URLError, e:
	print e.code
   else:
	# 200
	body = resp.read()
	return body;
   return None;

# Store the cookies and create an opener that will hold them
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# Add our headers
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36')]

# Install our opener (note that this changes the global opener to the one
# we just made, but you can also just call opener.open() if you want)
urllib2.install_opener(opener)

url = 'https://api.hivehome.com/v5/login'
payload = {
  'username':username,
  'password':password
  }

# Login
makeRequest(url,payload)

# Get HubID - Only taking the 1st into account!
opener.addheaders = [('X-Requested-With', 'XMLHttpRequest')];
url = "https://api.hivehome.com/v5/users/%s/hubs" %username
body = makeRequest(url,None)
#print body
temp = json.loads(body)
hubid = temp[0]['id']
mqttsend("/devices/"+temp[0]['name']+"/id",temp[0]['short_id'],0)

#print "Hub ID = ",hubid
#print "--------------"

# Get Device info
url = 'https://api.hivehome.com/v5/users/%s/hubs/%s/devices' %(username, hubid)
body = makeRequest(url,None)
devices = json.loads(body)
#print "--------------"
#print "Devices found:"
#print body
#print "--------------"
#print

for index in range(len(devices)):

	devtype = devices[index]['type']
	if devtype.startswith("HAHVAC"):
		devtype=devtype[6:]
	
	mqttsend("/devices/"+devtype+"/battery",devices[index]['channels']['battery'],0)
	mqttsend("/devices/"+devtype+"/batteryPercentage",devices[index]['channels']['batteryPercentage'],0)
	mqttsend("/devices/"+devtype+"/temperature",devices[index]['channels']['temperature'],0)
	mqttsend("/devices/"+devtype+"/signal",devices[index]['channels']['signal'],0)  

	if devtype.startswith("Thermostat"):
		hubmac= devices[index]['id']

#print "The Receiver MacID = ",hubmac
#print "--------------"

# Get heating control info - nothing useful here that is not in schedule
#opener.addheaders = [('X-Requested-With', 'XMLHttpRequest')];
#url = 'https://api.hivehome.com/v5/users/%s/widgets/climate/%s/control' %(username, hubmac)
#temp = json.loads(body)
#print body
#print "--------------"

#Get control schedule info

url = 'https://api.hivehome.com/v5/users/%s/widgets/climate/%s/controls/schedule' %(username, hubmac)
body = makeRequest(url,None)
temp = json.loads(body)

mqttsend("/heating/control",temp['control'],1)
mqttsend("/heating/mode",temp['mode'],1)  

#print body
#print "--------------"

# Get hotwater control info - nothing extra than the shown in schedule
#opener.addheaders = [('X-Requested-With', 'XMLHttpRequest')];
#url = 'https://api.hivehome.com/v5/users/%s/hubs/%s/devices/hotwatercontroller/%s/controls' %(username,hubid, hubmac)
#body = makeRequest(url,None)
#temp = json.loads(body)
#print body
#watercontrol = temp['current']
#print "Hotwater Control mode = ",watercontrol
#print "--------------"

#Get HW control schedule info 

url = 'https://api.hivehome.com/v5/users/%s/hubs/%s/devices/hotwatercontroller/%s/controls/schedule' %(username,hubid, hubmac)
body = makeRequest(url,None)
print "--------------"
print "result from hotwater call:"
print body
print "--------------"
print
temp = json.loads(body)

mqttsend("/hotwater/control",temp['control'],1)
mqttsend("/hotwater/mode",temp['onOffState'],1)  

# Get timestamp for record
mqttsend("/updated",time.time(),1) 

# Get temperature (weather) data for inside and out
url = "https://api.hivehome.com/v5/users/%s/widgets/temperature" %username
body = makeRequest(url,None)
#print body

weather = json.loads(body)
mqttsend("/heating/temperature",weather['inside']['now'],1) 
mqttsend("/weather/temperature",weather['outside']['now'],1) 
mqttsend("/weather/description",weather['outside']['weather']['description'],1)

# Get heating target temperature
url = "https://api.hivehome.com/v5/users/%s/widgets/climate/targetTemperature" %username
body = makeRequest(url,None)
#print body
target = json.loads(body)
mqttsend("/heating/target",target['temperature'],1) 


mqttc.disconnect()
# Logout
url = 'https://api.hivehome.com/v5/logout'
payload = {
  'username':username,
  'password':password
  }
makeRequest(url,payload)
