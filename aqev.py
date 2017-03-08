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
#import Tkinter
#from tkinter import ttk
from tkinter import *
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
#led_red = 5 # led on digital x
#grovepi.pinMode(led_red,"OUTPUT")


#- STOCKAGE SUR INTERNET
# Initial State settings
BUCKET_NAME_AQ = "Air Quality Monitoring"
BUCKET_KEY_AQ = "20070308-EV"
# intial state access key for jgailleur@hotmail.com
ACCESS_KEY = "0Vcs79QnlzNa7tO7Bn1sJ0LHgzyuTJaj"


# global variables to the application
    
DEBUG = False


# stream online to Initial State or not
stream_online = True



#################################
# AIR QUALITY APPLICATION CLASS
#################################
class AirQualityApp(Frame):

    # global constants

    
    # Set the time between sensor reads
    SECONDS_BETWEEN_READS = 30



    # -----------------------------------
    def __init__(self):

        # monitoring stopped
        self.sensorMonitoring = False


        # SENSORS OBJECT CREATION AND INITIALIZATION
        self.air_quality_sensor = grove_sensor_oo_lib.AirQualitySensor(0) # air quality on analog port 0
        self.gas_sensor_MQ2 = grove_sensor_oo_lib.GasSensor(2) # MQ2 on Analog port 2
        self.co2_sensor = grove_sensor_oo_lib.CO2SensorSerial()
        self.dust_sensor = grove_sensor_oo_lib.DustSensor(2, AirQualityApp.SECONDS_BETWEEN_READS)
        # Temperatures and humidity to add


        # DATA STREAM CREATION FOR SENDING DATA TO INITIAL STATE
        # open the streamer
        if (stream_online):
            self.streamer_aq = Streamer(bucket_name=BUCKET_NAME_AQ, bucket_key=BUCKET_KEY_AQ, access_key=ACCESS_KEY)

        Frame.__init__(self)
        self.createGUI()

        
        
    # -----------------------------------
    # ALL SENSORS DATA READING
    # -----------------------------------
    def readSensors(self):
        # Harmful gas
        air_quality_sensor_value = self.air_quality_sensor.readAirQuality()
        air_type_string = self.air_quality_sensor.getAirQualityStringValue(air_quality_sensor_value)
        airquality_text = str(air_quality_sensor_value)+" ("+ str(air_type_string) +")"
        self.airQualityLabelValue.set(airquality_text)
        print("Harmful gas: "+airquality_text)

        #--------------------------------------
        # reading and dis[play of gases density
        gas_MQ2_density = self.gas_sensor_MQ2.readGasDensity()
        self.gasMQ2Value.set(str(gas_MQ2_density))

        print("Combustible gases (H2, LPG, CH4, CO, Alcohol, Propane & smoke (MQ2), 200-10000, lower better %d" %(gas_MQ2_density))

        #--------------------------------------
        # reading CO2
        co2_concentration = self.co2_sensor.readConcentration()
        self.co2Value.set(str(co2_concentration))
        print("Carbon dioxide (CO2) PPM around 400: %d ppm" %(co2_concentration))

        #--------------------------------------
        # dust particules
        dust_concentration = self.dust_sensor.readConcentration()
        if (dust_concentration>0):
            print("Dust particule concentration: %d" %(dust_concentration))
            self.dustValue.set(str(dust_concentration))
        else:
            print("Dust particule: no reading")
            
        if self.dust_sensor.getNbConsecutiveNoReading() > 10:
            print ("WARNING: no reading dustsensor %d" %(self.dust_sensor.getNbConsecutiveNoReading()))
            self.dustValue.set("Problème de lecture")
            # reinit
            self.dust_sensor = grove_sensor_oo_lib.DustSensor(2, AirQualityApp.SECONDS_BETWEEN_READS)



        #------------------------------------------------------
        # stream data points
        # ----- Gases ----
        if (stream_online):
            self.streamer_aq.log("Harmfull Gas (1-900)",air_quality_sensor_value)
            self.streamer_aq.log("Combustibles Gas (200-10,000)",gas_MQ2_density)
            self.streamer_aq.log("CO2 (0-20,000)", co2_concentration)

            # ---------- PARTICULE ------------
            # stream dust particule information
            if (dust_concentration>0):
                self.streamer_aq.log("Dust particule (0-8,000)", dust_concentration)

            self.streamer_aq.flush()


    # -----------------------------------
    # CREATION OF THE DESKTOP GUI 
    # -----------------------------------
    def createGUI(self):
        #main window
        #self.main_window = Tk()
        self.myFont = tkFont.Font(family = 'Verdana', size = 18, weight = 'bold')
        self.mySmallFont = tkFont.Font(family = 'Verdana', size = 12, weight = 'bold')
        self.myLargeFont = tkFont.Font(family = 'Verdana', size = 24, weight = 'bold')

        self.master.title("Système de mesure de la qualité de l'air")       #----
        #self.master.title("Program window")

        self.master.geometry("800x480+0+0")

        #ledButton = Button(main_window, text = "LED ON", font = myFont, command = ledON, height = 2, width =8 )
        #ledButton.pack()

        #self.startMonitoringButton = Tkinter.Button(self.main_window, text = "Démarrer", font = self.myFont, command = self.startMonitoringCallback, height = 2, width =8 )
    
        #create the grid
        self.master.rowconfigure( 0, weight = 2 )
        self.master.columnconfigure( 0, weight = 2 )
        self.grid(stick=W+E+N+S)

        #set up the widgets
        row_value=0

        self.informationLabelValue1=StringVar()
        Label(self, textvariable=self.informationLabelValue1, font = self.myFont).grid(row=row_value,sticky=W)
        self.informationLabelValue1.set("Appuyer sur <Démarrer>")

        self.informationLabelValue3=StringVar()
        Label(self, textvariable=self.informationLabelValue3, font = self.myFont).grid(row=row_value, column=1, sticky=W)
        self.informationLabelValue3.set(" ")

        row_value = row_value +1
        Label(self, text="Date & heure Dernière mesure", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        self.informationLabelValue2=StringVar()
        Label(self, textvariable=self.informationLabelValue2, font = self.myFont).grid(row=row_value, column=1, sticky=W)
        self.informationLabelValue2.set(" aucune")

        row_value = row_value +1
        Label(self, text="(c) Emma & Victoria ", font = self.mySmallFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)

        # Sensors 1: air quality
        row_value = row_value +1
        Label(self, text="Gaz dangereux (1-900):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=W)
        self.airQualityLabelValue=StringVar()
        airQualityLabel=Label(self, textvariable=self.airQualityLabelValue, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.airQualityLabelValue.set(" - ")

        # Sensors 2: MQ2
        row_value = row_value +1
        Label(self, text="Gaz inflammables (200-10,000):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=W)
        self.gasMQ2Value=StringVar()
        gasMQ2Label=Label(self, textvariable=self.gasMQ2Value, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.gasMQ2Value.set(" - ")

        # Sensors 3: CO2
        row_value = row_value +1
        Label(self, text="CO2 (0-20,000):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=W)
        self.co2Value=StringVar()
        gasMQ2Label=Label(self, textvariable=self.co2Value, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.co2Value.set(" - ")

        # Sensors 4: DUST
        row_value = row_value +1
        Label(self, text="Particules fines (0-8,000):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=W)
        self.dustValue=StringVar()
        gasMQ2Label=Label(self, textvariable=self.dustValue, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.dustValue.set(" - ")

        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)

        # buttons
        row_value = row_value +1
        self.startButtonLabel=StringVar()
        Button(self, textvariable =self.startButtonLabel, font = self.myFont, command = lambda: self.startMonitoringCallback(), height = 2, width =8 ).grid(row=row_value, column=0, sticky=W+S)
        self.startButtonLabel.set("Démarrer")
        Button(self, text = "Quitter", font = self.myFont, command = lambda: self.quitCallback(), height = 2, width =8 ).grid(row=row_value, column=1, sticky=W+S)


        '''
        #main input box
        self.inputBox=Text(self) 
        self.inputBox.grid(row=1, sticky=W+E+S+N)
        self.inputBox.insert(END, 'Example content\ngoes here')
        #other buttons
        Button(self, text="Run", command=self.startMonitoringCallback).grid(row=3, sticky=W)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
    

        self.startMonitoringButton = Button(self, text = "Démarrer", font = self.myFont, command = lambda: self.startMonitoringCallback(), height = 2, width =8 )
#        self.startMonitoringButton.pack()
        self.optionsButton = Button(self, text = "Options", font = self.myFont, command = lambda: self.optionsCallback(), height = 2, width =8 )
#        self.optionsButton.pack()
        self.quitButton = Button(self, text = "Quit", font = self.myFont, command = lambda: self.quitCallback(), height = 2, width =8 )
#        self.quitButton.pack()
        '''

        #style=ttk.Style()
        #style.configure("BW.TLabel", foreground="black", background="white")

        '''
        self.airQualityLabelValue=StringVar()
        airQualityLabel=Label(self, textvariable=self.airQualityLabelValue, font = self.myFont)
#        airQualityLabel.pack()
        self.airQualityLabelValue.set("Air Quality value: ")
        '''
        #END createGUI


    # -----------------------------------
    # CALLBACK
    # -----------------------------------
    def startMonitoringCallback(self):
        if (self.sensorMonitoring == True):
            # stop the capture
            self.sensorMonitoring = False
            self.startButtonLabel.set("Démarrer")
            self.informationLabelValue1.set("Appuyer sur <Démarrer>")
            #self.informationLabelValue2.set(" ")
            self.informationLabelValue3.set(" ")


        else:
            # start the capture
            self.sensorMonitoring = True
            self.startButtonLabel.set("Arrêter")
            self.informationLabelValue1.set("Mesure en cours...")
            

    # -----------------------------------
    # CALLBACK
    # -----------------------------------

    def quitCallback(self):
        self.infiniteLoop=False
        self.master.quit()



    # -----------------------------------
    # MAIN LOOP
    # -----------------------------------
    def mainLoop(self):


        # Init last time the reading was done
        last_reading_time_seconds = 0 #time.mktime(datetime.datetime.utcnow().timetuple())

        self.infiniteLoop=True

        # infinite loop
        while (self.infiniteLoop):
    
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
                if (self.sensorMonitoring)  and (now_seconds >= last_reading_time_seconds + AirQualityApp.SECONDS_BETWEEN_READS):

                    print ("---------------------")
                    print("Now (utc): "+str(now))
                    print ("---------------------")

                    # --- read the sensors, send to Internet and print in the terminal ---
                    self.readSensors()
                    self.informationLabelValue2.set(str(now))
                    last_reading_time_seconds = now_seconds

                    # endif data reading
                elif (self.sensorMonitoring):
                    # next capture
                    self.informationLabelValue3.set("Prochaine mesure dans %d s" %(round(last_reading_time_seconds + AirQualityApp.SECONDS_BETWEEN_READS - now_seconds)))    
                    
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
                self.master.update_idletasks()
                self.master.update()

            # endtry
            except KeyboardInterrupt:	# Turn LED off before stopping
                grovepi.digitalWrite(led_red,0)
                self.master.quit()
                break

            except IOError:
                print ("Error")


        # end while


#----------------------------------
# MAIN PROGRAM
#----------------------------------
if __name__ == '__main__':

#    main_window = Tk()
#    airQualityApp = AirQualityApp(main_window)
    AirQualityApp().mainLoop() # custom mainloop for data acquisition









