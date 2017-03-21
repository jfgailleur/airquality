#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Air quality monitoring


# LIBRARIES WE ARE USING
import grovepi
import os
import time
from ISStreamer.Streamer import Streamer
import atexit
import datetime

# Connect the CO2 sensor to the RPISER port on the GrovePi
import grove_co2_lib

#-------------------
# DEBUG FLAG
DEBUG = False

#-------------------
# 50% = .5, 100% = 1, 200% =2 ...
MAX_PERCENT_ERROR = 3

#-------------------
# remove spike
# max_percent_error: number between 1 and x%, e.g. 100% = 1
## return new_value if value between previous_value+(previous_value*max_percent_error)
# or return new_value if previous_value == 0 (for initialization)
def removeSpike(previous_value, new_value, max_percent_error):
    if (DEBUG):
        print ("GroveSensor::removeSpike")
    if (previous_value == 0):
        return new_value
    if new_value > (previous_value+(previous_value*max_percent_error)):
        return previous_value
    elif new_value < (previous_value-(previous_value*max_percent_error)):
         return previous_value
    else:
         return new_value

#-------------------
class GroveSensor:
#     port = -1
#     type =
    pass


#-------------------
#---------- TEMPERATURE and HUMIDITY SENSOR -----------------
class TempAndHumSensor(GroveSensor):

    # --------- User Settings ---------
    # The DHT_SENSOR_TYPE below may need to be changed depending on which DHT sensor you have:
    #  0 - DHT11 - blue one - comes with the GrovePi+ Starter Kit
    #  1 - DHT22 - white one, aka DHT Pro or AM2302
    #  2 - DHT21 - black one, aka AM2301
    self.DHT_SENSOR_TYPE = 1
    # Connect the DHT sensor to one of the digital pins (i.e. 2, 3, 4, 7, or 8)
    self.dht_sensor_port = 0

    # init
    def __init__(self, port):
        # port
        self.dht_sensor_port = port
        self.last_value =0


    def readTempAndHum(self):

        # get temperature and humidity
        self.temp = 0
        self.hum = 0
        [self.temp,self.hum] = grovepi.dht(dht_sensor_port, self.DHT_SENSOR_TYPE)

    def getTemp(self):
        return self.temp

    def getHum(self):
        return self.hum


#-------------------
#---------- CO2 SENSOR -----------------
class CO2SensorSerial(GroveSensor):

    # init
    def __init__(self):
        # connect to the CO2 sensor
        self.co2= grove_co2_lib.CO2()
        self.last_value =0


    def reset(self):
        self.last_value =0
        


    def readConcentration(self):

        co2_ppm = self.last_value

        try:
            # get CO2 concentration
            [co2_ppm, co2_temp]= self.co2.read()
            # read again if number too high
            if (co2_ppm > 20,000):
                time.sleep(.5)
                self.co2= grove_co2_lib.CO2()
                [co2_ppm, co2_temp]= self.co2.read()
                # if still too high
#                if (co2_ppm > 20,000):
#                   co2_ppm = 0 
            

            if (DEBUG):
                print("CO2 Conc: %d ppm\t Temp: %d C" %(co2_ppm,co2_temp))
            #remove spike
            co2_ppm = removeSpike(self.last_value, co2_ppm, MAX_PERCENT_ERROR)
            self.last_value = co2_ppm

            return (co2_ppm)
        except:
            return (co2_ppm)



#-------------------          
class DustSensor(GroveSensor):
#    lowpulseoccupancy=-1
#    new_val=-1
#    dust_concentration=0

    # initialization, D2 port, sample time in s
    def __init__(self, port,sampletime_s):
        if (DEBUG):
            print ("DustSensor::__init__")
        self.port=port
        self.dustsensor_sampletime_ms = sampletime_s*1000

        atexit.register(grovepi.dust_sensor_dis)
        grovepi.dust_sensor_en()

        self.last_value =0
        self.nb_consecutive_no_reading=0


    def getNbConsecutiveNoReading(self):
        return self.nb_consecutive_no_reading

    # read data from the sensor and return the concentration
    # return dust concentration as integer, 0 if no reading
    def readConcentration(self):
        dust_concentration = self.last_value
        if (DEBUG):
            print ("dust_concentration  %d" %(dust_concentration))
            print ("self.last_value %d" %(self.last_value))
        try:
            # reading dust sensor
            lowpulseoccupancy=-1
            [new_val,lowpulseoccupancy] = grovepi.dustSensorRead()
            if (DEBUG):
                print ("new_val %d" %(new_val))
                print ("lowpulseoccupancy %d" %(lowpulseoccupancy))

            # calculate concentration: http://www.howmuchsnow.com/arduino/airquality/grovedust/
            if (new_val):
                ratio = lowpulseoccupancy /(self.dustsensor_sampletime_ms*1.0) # Integer percentage 0 to 100
                dust_concentration = round((1.1*pow(ratio,3))-(3.8*pow(ratio,2))+(520*ratio)+0.62,0) # using spec sheet curve
                if (DEBUG):
                    print ("dust_concentration read %d" %(dust_concentration))
                    print ("self.last_value %d" %(self.last_value))
          
                dust_concentration = removeSpike(self.last_value, dust_concentration, MAX_PERCENT_ERROR)
                if (dust_concentration > 10000):
                    dust_concentration =0
                self.last_value = dust_concentration

                if (DEBUG):
                    print ("dust_concentration computed %d" %(dust_concentration))
                self.nb_consecutive_no_reading=0

            else:
                dust_concentration = self.last_value
                self.nb_consecutive_no_reading=self.nb_consecutive_no_reading+1
 
            if (DEBUG):
                print ("dust_concentration  %d" %(dust_concentration))
                print ("self.last_value %d" %(self.last_value))

            # dust_concentration
            return dust_concentration

        except:
            self.nb_consecutive_no_reading=self.nb_consecutive_no_reading+1
            return dust_concentration
    
#endofclass DustSensor
    

#---------- AIR QUALITY SENSOR -----------------
# NOTE: # Wait 2 minutes for the sensor to heat-up
# Connect the Grove Air Quality Sensor to analog port A0
# SIG,NC,VCC,GND
class AirQualitySensor(GroveSensor):
#    air_quality_sensor_value = 0 # air quality sensor
#    last_value = 0

    def __init__(self, port):
        self.port=port
        grovepi.pinMode(self.port,"INPUT")
        self.last_value =0

    def readAirQuality(self):
        air_quality_sensor_value = self.last_value

        try:
            # Get air quality sensorS value
            air_quality_sensor_value = grovepi.analogRead(self.port)
            #remove spike
            air_quality_sensor_value = removeSpike(self.last_value, air_quality_sensor_value, MAX_PERCENT_ERROR)
            self.last_value = air_quality_sensor_value

            return (air_quality_sensor_value)
        except:
            return (air_quality_sensor_value)


    def getAirQualityStringValue(self, air_quality_sensor_value): 
        air_quality_type = "unknown"
        if air_quality_sensor_value > 700:
            air_quality_type = "danger" #"High pollution"
        elif air_quality_sensor_value > 300:
            air_quality_type = "pollution" #"low pollution"
        elif air_quality_sensor_value > 0:
            air_quality_type = "air frais" #"Fresh air"
        return (air_quality_type)


#---------- GAZ SENSOR -----------------
# gas sensor
# There are 5 gas sensors
# MQ2 - Combustible Gas, Smoke*
# MQ3 - Alcohol Vapor
# MQ5 - LPG, Natural Gas, Town Gas
# MQ9 - Carbon Monoxide, Coal Gas, Liquefied Gas*
# 02 - Oxygen
# The sensitivity can be adjusted by the onboard potentiometer
# http://www.seeedstudio.com/wiki/Grove_-_Gas_Sensor
class GasSensor(GroveSensor):

    def __init__(self, port):
        if (DEBUG):
            print ("GasSensor::__init__")

        self.port=port
        grovepi.pinMode(self.port,"INPUT")
        self.last_value =0

        if (DEBUG):
            print ("self.port %d" %(self.port))

    def readGasDensity(self):
        gas_density = self.last_value
        try:
            if (DEBUG):
                print ("readGasDensity  --  self.port %d" %(self.port))

            # Get gas sensor value
            gas_sensor_value = grovepi.analogRead(self.port)

            if (DEBUG):
                print ("gas_sensor_value %d" %(gas_sensor_value))
    
            # Calculate gas density - large value means more dense gas
#            gas_density = round((float)(gas_sensor_value / 1024), 0)
            gas_density = gas_sensor_value

            if (DEBUG):
                print ("gas_density %d" %(gas_density))

            # remove spike
            gas_density = removeSpike(self.last_value, gas_density, MAX_PERCENT_ERROR)
            self.last_value = gas_density

            if (DEBUG):
                print ("gas_density  %d" %(gas_density))
                print ("self.last_value %d" %(self.last_value))
    

            return (gas_density)
        
        except:
            return (gas_density)

"""
#------------------------------------------------------
# MAIN  (TEST PROGRAM)         
#------------------------------------------------------
# leds
led_red = 6 # red on digital 5
grovepi.pinMode(led_red,"OUTPUT")
#------------------------------------------------------

SECONDS_BETWEEN_READS = 20

dust_sensor = DustSensor(2, SECONDS_BETWEEN_READS)
air_quality_sensor = AirQualitySensor(0) # air quality on analog port 0
gas_sensor_MQ9 = GasSensor(1) # MQ9 on Analog port 1
gas_sensor_MQ2 = GasSensor(2) # MQ2 on Analog port 2

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
        air_type_string = air_quality_sensor.getAirQualityStringValue()
        print("Air quality: "+str(air_type_string)+" (%d)" %(air_quality_sensor_value))

        dust_concentration = dust_sensor.readConcentration()
        if (dust_concentration>0):
            print("Dust particule concentration: %d" %(dust_concentration))
        else:
            print("Dust particule: no reading")

        gas_MQ2_density = gas_sensor_MQ2.readGasDensity()
        gas_MQ9_density = gas_sensor_MQ9.readGasDensity()

        print("Combustible gases (H2, LPG, CH4, CO, Alcohol, Propane & smoke (MQ2), 200-10000, lower better %d" %(gas_MQ2_density))
        print("Gases LPG, CO, CH4 (MQ9), 200-10000, lower better %d" %(gas_MQ9_density))

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

"""


