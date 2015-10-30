# hive2mqtt
Python code to pull data from Hive Active Home and publish to MQTT

Need to install Paha Python MQTT client (using PIP)
* pip install paho-mqtt

Install PIP if it is not installed. 
Raspberry instructions here: https://www.raspberrypi.org/documentation/linux/software/python.md


The Login information is stored in hive_config.json. Make sure that you edit hive2mqtt.py to point to this file.

Example hive_config.json

{
  "config": [
	{ "username":"fred@fredbloogs.com" },
	{ "password":"bloggs1234" },
	{ "mqtthost":"192.168.1.50"},
	{ "mqttport":"1883" },
	{ "mqttuser":"fred" },
	{ "mqttpass":"bloggsmqttpass" },
	{ "mqtttopic":"House/Hive" }
    ]
} 

MQTTtopic is the root topic that the application will publish to

example:
TOPIC	DATA	RETAIN

House/Hive/devices/Hive Hub/id HWT-050 0
House/Hive/devices/TemperatureSensorSLT3/battery 5.9 0
House/Hive/devices/TemperatureSensorSLT3/batteryPercentage 100 0
House/Hive/devices/TemperatureSensorSLT3/signal 100 0
House/Hive/devices/ThermostatSLR2/temperature 20.25 0
House/Hive/devices/ThermostatSLR2/signal 100 0
House/Hive/heating/control SCHEDULE 1
House/Hive/heating/mode HEAT 1
House/Hive/hotwater/control SCHEDULE 1
House/Hive/hotwater/mode ON 1
House/Hive/updated 1446228227.52 1
House/Hive/heating/temperature 20.3 1
House/Hive/weather/temperature 15.0 1
House/Hive/weather/description Partly Cloudy 1
House/Hive/heating/target 19.5 1


I can see when Boost is applied to Water but not Heating.... 

Use a CRON job or NodeRed to call:  python hive2mqtt.py

