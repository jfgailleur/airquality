# airquality

Monitoring of air quality


Air quality is defined by 1) gaz and 2) particules

1) gases

Air quality sensor (analog port): 
http://wiki.seeed.cc/Grove-Air_Quality_Sensor_v1.3/
Mainly detects harmful gases such as carbon monoxide, alcohol, acetone, thinner, formaldehyde. 
It cannot output specific data to describe target gases' concentrations quantitatively.

HCHO sensor (analog port):
http://wiki.seeed.cc/Grove-HCHO_Sensor/
Target gases: HCHO, Benzene, Toluene, Alcohol
Concentration of VOC gas in the air.

CO2 sensor (digital port)
http://wiki.seeed.cc/Grove-CO2_Sensor/
Infrared CO2 sensor, measurement range from 0-20000 PPM


2) Dust sensor

3) others sensors
Temperature and humidity


Main platform
- Raspberrry Pi Model 3
- GrovePi for connecting the sensors/actuators

Using Initialstate.com to send data monitored in the cloud and display graphs

