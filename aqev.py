#!/usr/bin/env python
#
# Air quality monitoring
# Science project based on RaspberryPi, GrovePi and Grove sensors and actuators
#
#


'''
## License

The MIT License (MIT)

Copyright (c) 2017 Emma Gailleur & Victoria Lapointe

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2015  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''


# LIBRARIES WE ARE USING
import grovepi
import os
import time
from ISStreamer.Streamer import Streamer
import atexit
import datetime


import grove_sensor_oo_lib

# Connect the CO2 sensor to the RPISER port on the GrovePi
import grove_co2_lib


#----------------------------------
# MAIN PROGRAM
#----------------------------------
# INITIALIZATION

#- STOCKAGE SUR INTERNET
# Initial State settings
BUCKET_NAME_AQ = "Air Quality Monitoring"
BUCKET_KEY_AQ = "20070301-EV"
# intial state access key for jgailleur@hotmail.com
ACCESS_KEY = "0Vcs79QnlzNa7tO7Bn1sJ0LHgzyuTJaj"

stream_online = False


# Set the time between sensor reads
SECONDS_BETWEEN_READS = 30


# SENSORS OBJECT CREATION AND INITIALIZATION
dust_sensor = grove_sensor_oo_lib.DustSensor(2, SECONDS_BETWEEN_READS)
air_quality_sensor = grove_sensor_oo_lib.AirQualitySensor(0) # air quality on analog port 0
gas_sensor_MQ9 = grove_sensor_oo_lib.GasSensor(1) # MQ9 on Analog port 1
gas_sensor_MQ2 = grove_sensor_oo_lib.GasSensor(2) # MQ2 on Analog port 2


# leds
led_red = 6 # red on digital 5
grovepi.pinMode(led_red,"OUTPUT")

# INIT TO SEND TO INTERNET
# open the streamer
streamer_aq = Streamer(bucket_name=BUCKET_NAME_AQ, bucket_key=BUCKET_KEY_AQ, access_key=ACCESS_KEY)


# infinite loop
while True:
    
    try:
        # LED OFF
        grovepi.digitalWrite(led_red,0)

        #------------------------------------------------------
        # MEASUREMENT
        # data acquisition
        now = datetime.datetime.utcnow()
        print ("---------------------")
        print("Now (utc): "+str(now))
        print ("---------------------")


        air_quality_sensor_value = air_quality_sensor.readAirQuality()
        air_type_string = air_quality_sensor.getAirQualityStringValue(air_quality_sensor_value)
        print("Air quality (1-900), lower better: "+str(air_type_string)+" (%d)" %(air_quality_sensor_value))

        dust_concentration = dust_sensor.readConcentration()
        if (dust_concentration>0):
            print("Dust particule concentration: %d" %(dust_concentration))
        else:
            print("Dust particule: no reading")
            
        if dust_sensor.getNbConsecutiveNoReading() > 10:
            print ("WARNING: no reading dustsensor %d" %(dust_sensor.getNbConsecutiveNoReading()))

        # reading and dis[play of gases density
        gas_MQ2_density = gas_sensor_MQ2.readGasDensity()
        gas_MQ9_density = gas_sensor_MQ9.readGasDensity()

        print("Combustible gases (H2, LPG, CH4, CO, Alcohol, Propane & smoke (MQ2), 200-10000, lower better %d" %(gas_MQ2_density))
        print("Gases LPG, CO, CH4 (MQ9), 200-10000, lower better %d" %(gas_MQ9_density))


        #------------------------------------------------------
        # stream data points
        # ----- Gases ----
        streamer_aq.log("Air quality (1 to 900), lower better",air_quality_sensor_value)
        streamer_aq.log("Combustibles gas & smoke (MQ2), lower better",gas_MQ2_density)
        streamer_aq.log("Combustibles gas & smoke (MQ9), lower better",gas_MQ9_density)
        # ---------- PARTICULE ------------
        # stream dust particule information
        if (dust_concentration>0):
            streamer_aq.log("Dust particule concentration (pcs/0.01cf), lower better", dust_concentration)

        streamer_aq.flush()
            

        #------------------------------------------------------
        # wait until next acquisition
        for i in range (1, SECONDS_BETWEEN_READS):
            grovepi.digitalWrite(led_red,1)
            time.sleep(.5)
            grovepi.digitalWrite(led_red,0)
            time.sleep(.5)

    # endtry

    except KeyboardInterrupt:	# Turn LED off before stopping
        grovepi.digitalWrite(led_red,0)
        break

    except IOError:
        print ("Error")


# end while


