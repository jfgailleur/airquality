#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Air quality monitoring
# Science project based on RaspberryPi, GrovePi and Grove sensors and actuators
#
#
## License: The MIT License (MIT)
#

# LIBRARIES WE ARE USING
import os
import time
from ISStreamer.Streamer import Streamer
import atexit
import datetime

# graphical user interface libraries
import Tkinter
#from tkinter import ttk
#from tkinter import *
#from tkinter.ttk import *
import tkFont

#dexter industries open source libraries
import grovepi
import grove_co2_lib

# project libraries
import grove_sensor_oo_lib





#def ledON():
#    print("LED button pressed")






# leds
led_red = 5 # led on digital x
grovepi.pinMode(led_red,"OUTPUT")


#- STOCKAGE SUR INTERNET
# Initial State settings
BUCKET_NAME_AQ = "Air Quality Monitoring"
BUCKET_KEY_AQ = "20070301-EV"
# intial state access key for jgailleur@hotmail.com
ACCESS_KEY = "0Vcs79QnlzNa7tO7Bn1sJ0LHgzyuTJaj"


# global variables to the application
    
DEBUG = False


# stream online to Initial State or not
stream_online = False



#################################
# AIR QUALITY APPLICATION CLASS
#################################
class AirQualityApp(Tkinter.Frame):

    # global constants

    
    # Set the time between sensor reads
    SECONDS_BETWEEN_READS = 30



    # -----------------------------------
    def __init__(self):

        # monitoring stopped
        self.sensorMonitoring = False


        # SENSORS OBJECT CREATION AND INITIALIZATION
        self.dust_sensor = grove_sensor_oo_lib.DustSensor(2, AirQualityApp.SECONDS_BETWEEN_READS)
        self.air_quality_sensor = grove_sensor_oo_lib.AirQualitySensor(0) # air quality on analog port 0
        self.gas_sensor_MQ9 = grove_sensor_oo_lib.GasSensor(1) # MQ9 on Analog port 1
        self.gas_sensor_MQ2 = grove_sensor_oo_lib.GasSensor(2) # MQ2 on Analog port 2

        # CO2 to add
        # Connect the CO2 sensor to the RPISER port on the GrovePi

        # Temperatures and humidity to add


        # DATA STREAM CREATION FOR SENDING DATA TO INITIAL STATE
        # open the streamer
        if (stream_online):
            streamer_aq = Streamer(bucket_name=BUCKET_NAME_AQ, bucket_key=BUCKET_KEY_AQ, access_key=ACCESS_KEY)

        Tkinter.Frame.__init__(self)
        self.createGUI()

        
        '''
        self.master.title("Program window")
        self.master.rowconfigure( 0, weight = 1 )
        self.master.columnconfigure( 0, weight = 1 )
        self.grid(stick=W+E+N+S)
        #set up the widgets
        Label(self, text="Instructions go here").grid(row=0,sticky=W)
        #main input box
        self.inputBox=Text(self) 
        self.inputBox.grid(row=1, sticky=W+E+S+N)
        self.inputBox.insert(END, 'Example content\ngoes here')
        #other buttons
        Button(self, text="Run", command=self.run).grid(row=3, sticky=W)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        '''
        
    # -----------------------------------
    # ALL SENSORS DATA READING
    # -----------------------------------
    def readSensors(self):
        air_quality_sensor_value = self.air_quality_sensor.readAirQuality()
        air_type_string = self.air_quality_sensor.getAirQualityStringValue(air_quality_sensor_value)
        airquality_text = "Air quality (1-900), lower better: "+str(air_type_string)+" ("+ str(air_quality_sensor_value)+")"
        print(airquality_text)
        self.airQualityLabelValue.set(airquality_text)

        dust_concentration = self.dust_sensor.readConcentration()
        if (dust_concentration>0):
            print("Dust particule concentration: %d" %(dust_concentration))
        else:
            print("Dust particule: no reading")
            
        if self.dust_sensor.getNbConsecutiveNoReading() > 10:
            print ("WARNING: no reading dustsensor %d" %(self.dust_sensor.getNbConsecutiveNoReading()))
            # reinit
            self.dust_sensor = grove_sensor_oo_lib.DustSensor(2, AirQualityApp.SECONDS_BETWEEN_READS)


        # reading and dis[play of gases density
        gas_MQ2_density = self.gas_sensor_MQ2.readGasDensity()
        gas_MQ9_density = self.gas_sensor_MQ9.readGasDensity()

        print("Combustible gases (H2, LPG, CH4, CO, Alcohol, Propane & smoke (MQ2), 200-10000, lower better %d" %(gas_MQ2_density))
        print("Gases LPG, CO, CH4 (MQ9), 200-10000, lower better %d" %(gas_MQ9_density))


        #------------------------------------------------------
        # stream data points
        # ----- Gases ----
        if (stream_online):
            streamer_aq.log("Air quality (1 to 900), lower better",air_quality_sensor_value)
            streamer_aq.log("Combustibles gas & smoke (MQ2), lower better",gas_MQ2_density)
            streamer_aq.log("Combustibles gas & smoke (MQ9), lower better",gas_MQ9_density)
            # ---------- PARTICULE ------------
            # stream dust particule information
            if (dust_concentration>0):
                streamer_aq.log("Dust particule concentration (pcs/0.01cf), lower better", dust_concentration)

            streamer_aq.flush()


    # -----------------------------------
    # CREATION OF THE DESKTOP GUI 
    # -----------------------------------
    def createGUI(self):
        #main window
        self.main_window = Tkinter.Tk()
        self.myFont = tkFont.Font(family = 'Verdana', size = 20, weight = 'bold')
        self.main_window.title("Système de mesure de la qualité de l'air")       #----
        self.main_window.geometry("800x480+0+0")

        #ledButton = Button(main_window, text = "LED ON", font = myFont, command = ledON, height = 2, width =8 )
        #ledButton.pack()

        #self.startMonitoringButton = Tkinter.Button(self.main_window, text = "Démarrer", font = self.myFont, command = self.startMonitoringCallback, height = 2, width =8 )
        self.startMonitoringButton = Tkinter.Button(self.main_window, text = "Démarrer", font = self.myFont, command = lambda: self.startMonitoringCallback(), height = 2, width =8 )
        self.startMonitoringButton.pack()
        self.optionsButton = Tkinter.Button(self.main_window, text = "Options", font = self.myFont, command = lambda: self.optionsCallback(), height = 2, width =8 )
        self.optionsButton.pack()
        self.quitButton = Tkinter.Button(self.main_window, text = "Quit", font = self.myFont, command = lambda: self.quitCallback(), height = 2, width =8 )
        self.quitButton.pack()

        #style=ttk.Style()
        #style.configure("BW.TLabel", foreground="black", background="white")

        self.airQualityLabelValue=Tkinter.StringVar()
        airQualityLabel=Tkinter.Label(textvariable=self.airQualityLabelValue, font = self.myFont)
        airQualityLabel.pack()
        self.airQualityLabelValue.set("Air Quality value: ")

        #END createGUI


    # -----------------------------------
    # CALLBACK
    # -----------------------------------
    def startMonitoringCallback(self):
        if (self.sensorMonitoring == True):
            self.sensorMonitoring = False
            #Change text
            #        startMonitoringButton.
        else:
            self.sensorMonitoring = True
    # -----------------------------------
    # CALLBACK
    # -----------------------------------
    def optionsCallback(self):
        pass

    def quitCallback(self):
        pass



    # -----------------------------------
    # MAIN LOOP
    # -----------------------------------
    def mainLoop(self):


        self.readSensors()
        last_reading_time_seconds = time.mktime(datetime.datetime.utcnow().timetuple())


        # infinite loop
        while True:
    
            try:
                # LED OFF
                # grovepi.digitalWrite(led_red,0)

                #------------------------------------------------------
                # MEASUREMENT
                # data acquisition
                now = datetime.datetime.utcnow()

                now_seconds = time.mktime(now.timetuple())
                if (DEBUG):
                    print("now_seconds:"+str(now_seconds))
                    print("last_reading_time_seconds:"+str(last_reading_time_seconds))
                    print("SECONDS_BETWEEN_READS:"+str(AirQualityApp.SECONDS_BETWEEN_READS))
                    
                    
            
                # do we read data this loop?
                if (now_seconds >= last_reading_time_seconds + AirQualityApp.SECONDS_BETWEEN_READS):

                    print ("---------------------")
                    print("Now (utc): "+str(now))
                    print ("---------------------")

                    # --- read the sensors ---
                    self.readSensors()
                    last_reading_time_seconds = now_seconds
                


                    # endif data reading
                    
                '''
                #------------------------------------------------------
                # wait until next acquisition
                for i in range (1, SECONDS_BETWEEN_READS):
                    grovepi.digitalWrite(led_red,1)
                    time.sleep(.5)
                    grovepi.digitalWrite(led_red,0)
                    time.sleep(.5)
                '''


                # main loop for TKinter
                self.main_window.update_idletasks()
                self.main_window.update()

            # endtry
            except KeyboardInterrupt:	# Turn LED off before stopping
                grovepi.digitalWrite(led_red,0)
                break

            except IOError:
                print ("Error")


        # end while


#----------------------------------
# MAIN PROGRAM
#----------------------------------
if __name__ == '__main__':

    airQualityApp = AirQualityApp()
    airQualityApp.mainLoop() # custom one for data acquisition









