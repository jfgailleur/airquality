#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Air quality monitoring
# Science project based on RaspberryPi, GrovePi and Grove sensors and actuators
#
## License: Open Source The MIT License (MIT)

# LIBRARIES WE ARE USING
import os
import time
from ISStreamer.Streamer import Streamer
import atexit
import datetime

# graphical user interface libraries
from tkinter import *
import tkFont

#dexter industries open source libraries
import grovepi
import grove_co2_lib

# project libraries
import grove_sensor_oo_lib

#- INTERNET DATA STORAGE AND ANALYSIS
# Initial State settings
BUCKET_NAME_AQ = "Air Quality Monitoring"
BUCKET_KEY_AQ = "20070308-EV"
# intial state access key for jgailleur@hotmail.com
ACCESS_KEY = "0Vcs79QnlzNa7tO7Bn1sJ0LHgzyuTJaj"

stream_online = True # stream online to Initial State or not


# DEBUG MODE
DEBUG = False

#################################
# AIR QUALITY APPLICATION CLASS
#################################
class AirQualityApp(Frame):

    # global constants
    SECONDS_BETWEEN_READS = 30 # Set the time between sensor reads for Dust sensor

    # -----------------------------------
    def __init__(self):

        # infinite loop and monitoring starting when app starts
        self.infiniteLoop = True
        self.sensorMonitoring = True


        # SENSORS CREATION AND INITIALIZATION
        self.air_quality_sensor = grove_sensor_oo_lib.AirQualitySensor(0) # air quality on analog port 0
        self.gas_sensor_MQ2 = grove_sensor_oo_lib.GasSensor(2) # MQ2 on Analog port 2
        self.co2_sensor = grove_sensor_oo_lib.CO2SensorSerial() # CO2 Sensor on Serial port
        self.dust_sensor = grove_sensor_oo_lib.DustSensor(2, AirQualityApp.SECONDS_BETWEEN_READS) #Dust sensor D2
        self.temp_hum_sensor = grove_sensor_oo_lib.TempAndHumSensor(4) # Temperatures and humidity on port D4

        # DATA STREAM CREATION FOR SENDING DATA TO INITIAL STATE
        # open the streamer
        if (stream_online):
            self.streamer_aq = Streamer(bucket_name=BUCKET_NAME_AQ, bucket_key=BUCKET_KEY_AQ, access_key=ACCESS_KEY)

        Frame.__init__(self)

        self.createGUI() # create the GUI


    # -----------------------------------
    # ALL SENSORS DATA READING
    # -----------------------------------
    def updateGUITempAndHumSensors(self):
        #
        pass


    def readTempAndHumSensors(self):
        self.temp_hum_sensor.readTempAndHum()
        self.inside_temperature = self.temp_hum_sensor.getLatestReadTemp()
        self.inside_humidity = self.temp_hum_sensor.getLatestReadHum()
        if (DEBUG):
            print("Inside temperature: "+str(self.inside_temperature))
            print("Inside humidity: "+str(self.inside_humidity))


    def updateGUIGasSensors(self):
        # harmful gas
        self.airQualityLabelValue.set(str(self.air_quality_sensor_value)+" ("+ str(self.air_type_string) +")")
        if (DEBUG):
            print("GUI Harmful gas: "+airquality_text)
        # combustible gas
        self.gasMQ2Value.set(str(self.gas_MQ2_density))
        if (DEBUG):
            print("GUI Combustible gases" +str(gas_MQ2_density))
        # CO2
        self.co2Value.set(str(self.co2_concentration))
        if (DEBUG):
            print("GUI Carbon dioxide (CO2) %d" %(self.co2_concentration))

    # -----------------------------------
    def readGasSensors(self, terminal_display):
        # Harmful gas
        self.air_quality_sensor_value = self.air_quality_sensor.readAirQuality()
        self.air_type_string = self.air_quality_sensor.getAirQualityStringValue(self.air_quality_sensor_value)

        # combustible gases
        self.gas_MQ2_density = self.gas_sensor_MQ2.readGasDensity()

        # reading CO2
        self.co2_concentration = self.co2_sensor.readConcentration()

        if (terminal_display):
            print("Harmful gases: "+str(self.air_quality_sensor_value)+" ("+ str(self.air_type_string) +")")
            print("Combustible gases, 200-10000, %d" %(self.gas_MQ2_density))
            print("Carbon dioxide (CO2): %d ppm" %(self.co2_concentration))
            

    # -----------------------------------
    def updateGUIDustSensors(self):
        if (self.dust_concentration>0):
            self.dustValue.set(str(self.dust_concentration))
            print("Dust particule concentration: %d" %(self.dust_concentration))
        else:
            # no GUI update, keep the previous value displayed
            print("Dust particule: no reading")

    def updateGUIDustSensorsWaiting(self):
        pass
#        if (self.dust_concentration>0):
#            self.dustValue.set(str(self.dust_concentration))
#        else:
#            self.dustValue.set("-")


    def readDustSensors(self):

        self.dust_concentration = self.dust_sensor.readConcentration()
#        self.dust_concentration = int(round(self.dust_sensor.readConcentration()))

        # renit if reading issues for 10 consecutive time            
        if self.dust_sensor.getNbConsecutiveNoReading() > 10:
            print ("WARNING: no reading dustsensor %d" %(self.dust_sensor.getNbConsecutiveNoReading()))
            self.dustValue.set("Problème de lecture")
            # reinit
            self.dust_sensor = grove_sensor_oo_lib.DustSensor(2, AirQualityApp.SECONDS_BETWEEN_READS)
        
    # -----------------------------------
    def readSubSetSensorsAndUpdateGUI(self):
        self.readGasSensors(False) # no printing in console
        self.updateGUIGasSensors()

       
    # -----------------------------------
    # ALL SENSORS DATA READING & Streaming
    # -----------------------------------
    def readSensorsAndUpdateGUIAndStream(self):

        self.readTempAndHumSensors()
        self.updateGUITempAndHumSensors()

        self.readGasSensors(True) # print value in console
        self.updateGUIGasSensors()
        
        self.readDustSensors()
        self.updateGUIDustSensors()

        self.streamOnlineData()

    # -----------------------------------
    # ONLINE STREAMING TO IOT PLATFORM
    # -----------------------------------
    def streamOnlineData(self):        

        #------------------------------------------------------
        # stream data points
        # ----- Gases ----
        if (stream_online):
            # -------- Gaz and CO2
            self.streamer_aq.log("Harmfull Gases (1-900)",self.air_quality_sensor_value)
            self.streamer_aq.log("Combustibles Gases (200-10,000)",self.gas_MQ2_density)
            self.streamer_aq.log("CO2 (0-20,000)", self.co2_concentration)

            # ---------- PARTICULE ------------
            # stream dust particule information
            if (self.dust_concentration>0):
                self.streamer_aq.log("Dust particule (0-8,000)", self.dust_concentration)

           # -------- temperature and humidity
            self.streamer_aq.log("Air temperature (Celcius)", self.inside_temperature)
            self.streamer_aq.log("Air humidity (%)", self.inside_humidity)

            # send all data
            self.streamer_aq.flush()

    # -----------------------------------
    # DISPLAY HOUR AND DATE 
    # -----------------------------------
    def displayDateaAdnTime(self, timenow):
        strtimenow = "{:02d}:{:02d}:{:02d}".format(timenow.hour, timenow.minute, timenow.second)
        self.informationLabelValue1.set(strtimenow)

    # -----------------------------------
    # CREATION OF THE DESKTOP GUI 
    # -----------------------------------
    def createGUI(self):
        self.myFont = tkFont.Font(family = 'Verdana', size = 16, weight = 'bold')
        self.mySmallFont = tkFont.Font(family = 'Verdana', size = 12, weight = 'bold')
        self.myLargeFont = tkFont.Font(family = 'Verdana', size = 18, weight = 'bold')

        self.master.title("Système de mesure de la qualité de l'air")
        self.master.geometry("800x480+0+0") # size of the main window

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
        self.informationLabelValue1.set("heure")

        self.informationLabelValue3=StringVar()
        Label(self, textvariable=self.informationLabelValue3, font = self.myFont).grid(row=row_value, column=1, sticky=W)
        self.informationLabelValue3.set(" ")

        row_value = row_value +1
#        Label(self, text="Date & heure de la dernière mesure:", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        self.informationLabelValue2=StringVar()
#        Label(self, textvariable=self.informationLabelValue2, font = self.myFont).grid(row=row_value, column=1, sticky=W)
#        self.informationLabelValue2.set(" aucune")

        row_value = row_value +1
        Label(self, text="(c) Emma Gailleur & Victoria Lapointe", font = self.mySmallFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
#        row_value = row_value +1
#        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)

        # Sensors 1: air quality
        row_value = row_value +1
        Label(self, text="Gaz dangereux (1-900):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=E)
        self.airQualityLabelValue=StringVar()
        airQualityLabel=Label(self, textvariable=self.airQualityLabelValue, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.airQualityLabelValue.set(" - ")

        # Sensors 2: MQ2
        row_value = row_value +1
        Label(self, text="Gaz inflammables (200-10 000):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=E)
        self.gasMQ2Value=StringVar()
        gasMQ2Label=Label(self, textvariable=self.gasMQ2Value, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.gasMQ2Value.set(" - ")

        # Sensors 3: CO2
        row_value = row_value +1
        Label(self, text="CO2 (0-20 000):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=E)
        self.co2Value=StringVar()
        gasMQ2Label=Label(self, textvariable=self.co2Value, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.co2Value.set(" - ")

        # Sensors 4: DUST
        row_value = row_value +1
        Label(self, text="Particules fines (0-8 000):", font = self.myLargeFont).grid(row=row_value, column=0, sticky=E)
        self.dustValue=StringVar()
        gasMQ2Label=Label(self, textvariable=self.dustValue, font = self.myLargeFont).grid(row=row_value, column=1, sticky=W)
        self.dustValue.set(" - ")

        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
        row_value = row_value +1
        Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
 #       row_value = row_value +1
 #       Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
 #       row_value = row_value +1
 #       Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)
 #       row_value = row_value +1
 #       Label(self, text=" ", font = self.myFont).grid(row=row_value, column=0, sticky=W)

        # buttons
        row_value = row_value +1
#        self.startButtonLabel=StringVar()
#        Button(self, textvariable =self.startButtonLabel, font = self.myFont, command = lambda: self.startMonitoringCallback(), height = 2, width =8 ).grid(row=row_value, column=0, sticky=W+S)
#        self.startButtonLabel.set("Démarrer")

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
    # CALLBACK FOR START BUTTON (NOT USED ANNYMORE)
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
            # reset
            self.reset()

            # start the capture
            self.sensorMonitoring = True
            self.startButtonLabel.set("Arrêter")
            self.informationLabelValue1.set("Mesure de la Qualité de l'air")
            

    # -----------------------------------
    # CALLBACK FOR QUIT BUTTON
    # -----------------------------------
    def quitCallback(self):
        self.infiniteLoop=False
        self.master.quit()

    # -----------------------------------
    # MAIN LOOP
    # -----------------------------------
    def mainLoop(self):
        
        now = datetime.datetime.utcnow()
        now_seconds = time.mktime(now.timetuple())
        last_reading_time_seconds=now_seconds

        # main inifite loop until quit        
        while (self.infiniteLoop):
            try:
                #------------------------------------------------------
                # DATE HOURS TIME
                now = datetime.datetime.utcnow()
                now_seconds = time.mktime(now.timetuple())
                
                # update time and date
                self.displayDateaAdnTime(now)
                
                # main loop for TKinter
                self.master.update_idletasks()
                self.master.update()

                if (DEBUG):
                    print("now_seconds:"+str(now_seconds))
                    print("last_reading_time_seconds:"+str(last_reading_time_seconds))
                    print("SECONDS_BETWEEN_READS:"+str(AirQualityApp.SECONDS_BETWEEN_READS))
                                
                #------------------------------------------------------
                # MEASUREMENT
                # do we read data this loop?
                if (self.sensorMonitoring)  and (now_seconds >= last_reading_time_seconds + AirQualityApp.SECONDS_BETWEEN_READS):

                    print ("---------------------")
                    print("Now (utc): "+str(now))
                    print ("---------------------")

                    # --- read the sensors, upate the GUI send to Internet and print in the terminal ---
                    self.readSensorsAndUpdateGUIAndStream()
                    
#                    self.informationLabelValue2.set(str(now))

                    # last reading is now!
                    last_reading_time_seconds = now_seconds

                #------------------------------------------------------
                # Update all sensor values beside dust
                elif (self.sensorMonitoring):
                    self.readSubSetSensorsAndUpdateGUI()

                    # next capture
                    self.informationLabelValue3.set("Particules maj dans %d s" %(round(last_reading_time_seconds + AirQualityApp.SECONDS_BETWEEN_READS - now_seconds)))    
                    
                # main loop for TKinter
                self.master.update_idletasks()
                self.master.update()

                # free some processor time
                time.sleep(.5)

            # endtry

            # QUIT IF CTRL C ON TERMINAL
            except KeyboardInterrupt:	
                self.master.quit()
                break

            except IOError:
                print ("Error")

        # end while

#----------------------------------
# MAIN PROGRAM
#----------------------------------
if __name__ == '__main__':
    # custom mainloop for sensor reading, online streaming & GUI events
    AirQualityApp().mainLoop() 









