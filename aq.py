
import grovepi
import os
import time
from ISStreamer.Streamer import Streamer

# Connect the CO2 sensor to the RPISER port on the GrovePi
import grove_co2_lib


# --------- User Settings ---------
# The DHT_SENSOR_TYPE below may need to be changed depending on which DHT sensor you have:
#  0 - DHT11 - blue one - comes with the GrovePi+ Starter Kit
#  1 - DHT22 - white one, aka DHT Pro or AM2302
#  2 - DHT21 - black one, aka AM2301
DHT_SENSOR_TYPE = 1
# Connect the DHT sensor to one of the digital pins (i.e. 2, 3, 4, 7, or 8)
DHT_SENSOR_PIN = 4

# Initial State settings
BUCKET_NAME_AQ = "Air Quality Monitoring"
BUCKET_KEY_AQ = "aq170213"

# intial state access key for jgailleur@hotmail.com
ACCESS_KEY = "0Vcs79QnlzNa7tO7Bn1sJ0LHgzyuTJaj"

# Set the time between sensor reads
MINUTES_BETWEEN_READS = 1
MINUTES = True # FALSE to MOVE TO SECONDs

#---------- AIR QUALITY SENSOR -----------------
# NOTE: # Wait 2 minutes for the sensor to heat-up
# Connect the Grove Air Quality Sensor to analog port A0
# SIG,NC,VCC,GND
air_sensor = 0 # air quality sensor
grovepi.pinMode(air_sensor,"INPUT")

#---------- CO2 SENSOR -----------------
# connect to the CO2 sensor
co2= grove_co2_lib.CO2()

#---------- HCHO SENSOR -----------------
# The sensitivity can be adjusted by the onboard potentiometer
# Connect the Grove HCHO Sensor to analog port A0
# SIG,NC,VCC,GND
hcho_sensor = 1
grovepi.pinMode(hcho_sensor,"INPUT")

# Vcc of the grove interface is normally 5v
grove_vcc = 5


# ---------------------------------

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
# ---------------------------------

# open the streamer
streamer_aq = Streamer(bucket_name=BUCKET_NAME_AQ, bucket_key=BUCKET_KEY_AQ, access_key=ACCESS_KEY)


while True:
    try:

        # data acquisition
        
        # Get air quality sensorS value
        air_quality_sensor_value = grovepi.analogRead(air_sensor)

        # get CO2
        [co2_ppm, co2_temp]= co2.read()

        # Get hcho sensor value
        hcho_sensor_value = grovepi.analogRead(hcho_sensor)
        # Calculate voltage
        hcho_voltage = (float)(hcho_sensor_value * grove_vcc / 1024)

        
        # stream data points
	streamer_aq.log("Air quality (1 to 900) lower better",air_quality_sensor_value)
	streamer_aq.log("Carbon dioxide (CO2) PPM around 400",co2_ppm)
	streamer_aq.log("Methanal(HCHO) PPM lower better",hcho_sensor_value)

        streamer_aq.flush()

        # Display on screen        
        if air_quality_sensor_value > 700:
            air_quality_type = "High pollution"
        elif air_quality_sensor_value > 300:
            air_quality_type = "Low pollution"
        else:
            air_quality_type = "Fresh air"
            
        print("Air quality: "+air_quality_type+" (%d)" %(air_quality_sensor_value))


	print("CO2 Conc: %d ppm\t Temp: %d C" %(co2_ppm,co2_temp))

        print("HCHO Value: ", hcho_sensor_value, " voltage =", hcho_voltage)


        # wait until next acquisition
        if (MINUTES):
            time.sleep(60*MINUTES_BETWEEN_READS)
        else:
            time.sleep(MINUTES_BETWEEN_READS)
            

    except IOError:
        print ("Error")


# end while


