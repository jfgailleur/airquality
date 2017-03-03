airquality

# Monitoring of air quality

## Introduction
Air quality is defined by 1) gases and 2) particules.

## RaspberryPi platform

# Hardware
* Low power consumption v2 model b
* Faster, less caring about consumption v3, model B with integrated WIFI 
* Sensors and Actuators using Grove Standards
* Grove interface using [GrovePi board] (https://www.dexterindustries.com/grovepi/) from Dexter Industies

# Software
OS: Dexter Rasbian Jessie version ?
GrovePi libraries

# AirQuality Application
Program written in Python with repository in GitHub

## Initial Configuration and Update
In a separate thread of the main one, so it's not blocking
1) If can connect to the Internet, 
* send self identification (unique identifer)
* ask for new configuration and update if necassary
* ask for new code and update itself if necessary
Considerations:
- configuration or code update first?
- security to ensure integrity, and avoid man in the middle attack, SSL and more
2) if cannot connect, scan wifi, try to connect to the open ones
3) if still cannot connect, ask for connecting

## Local Data storage
DB, e.g. SQL lite or flat files direct
Important to have a rotating buffer, i.e. when there is no more space, it writers 

## Human inputs/outputs
Human inputs: 
* E.g. Power on/off, start/stop measuring, enable/disable sending to Internet platform, enable/disable recording on local file 
* low cost and low consumption: Grove buttons
* otherwise: touch screen LCD with software buttons
Human outputs:
* E.g. informing current operations, display what are the current 
* low cost and low consumption: leds, or small screens like two lines small grove LCD
* otherwise: touch screen LCD with programming in TKinter (GUI python defacto framework)

## Online storage and reporting (Iot Platform)
Currently using InitialState.com

## Gas Sensors
### [Air quality sensor] (http://wiki.seeed.cc/Grove-Air_Quality_Sensor_v1.3/) 
Mainly detects harmful gases such as carbon monoxide, alcohol, acetone, thinner, formaldehyde. 
It cannot output specific data to describe target gases' concentrations quantitatively.
Type: analog port 

### [HCHO sensor] (http://wiki.seeed.cc/Grove-HCHO_Sensor/)
Target gases: HCHO, Benzene, Toluene, Alcohol
Concentration of VOC gas in the air.
Type: analog port 

### [CO2 sensor] (http://wiki.seeed.cc/Grove-CO2_Sensor/)
Infrared CO2 sensor, measurement range from 0-20000 PPM
400 is the average on earth [source] (https://en.wikipedia.org/wiki/Carbon_dioxide_in_Earth's_atmosphere)
Type: digital port 

### [MQ2 sensor] (http://wiki.seeed.cc/Grove-Gas_Sensor-MQ2/)
H2, LPG, CH4, CO, Alcohol, Smoke or Propane
200-10000 ppm
Type: analog port 

### [MQ9 sensor] (http://wiki.seeed.cc/Grove-Gas_Sensor-MQ9/)
LPG, CO, CH4
200-10000 ppm
Type: analog port 

## [Dust sensor] (http://wiki.seeed.cc/Grove-Dust_Sensor/, "Dust Sensor Seeed Wiki")
Detectable range of concentration 0 ~ 8000 pcs/0.01cf

## Other sensors
### Temperature and humidity Sensor

### GPS sensor if portable

## Power
* on socket AC/DC adaptor 5V 2A
* portable: Lipo battery 5v 10A, plus lipo usb charger plus solar panel 5V, 2W or 3W

