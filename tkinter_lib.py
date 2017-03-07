#from Tkinter import *
import Tkinter
import tkFont


# some examples
# https://docs.python.org/2/library/tkinter.html

class MainApp(frame):

    def __init__(self, parent=None):
        Frame.__init__(self, parent, background="white")
        self.parent=parent
        # self.parent.title(














'''
win = Tkinter.Tk()



def ledON():
	print("LED button pressed")
"""
        if GPIO.input(40) :
 		GPIO.output(40,GPIO.LOW)
		ledButton["text"] = "LED ON"
	else:
		GPIO.output(40,GPIO.HIGH)
                ledButton["text"] = "LED OFF"
"""

def exitProgram():
	print("Exit Button pressed")
	win.quit()	

#if __name__ == '__main__':


try:
    myFont = tkFont.Font(family = 'Helvetica', size = 36, weight = 'bold')


    win.title("First GUI")  
    win.geometry('800x480')

    exitButton  = Button(win, text = "Exit", font = myFont, command = exitProgram, height =2 , width = 6) 
    exitButton.pack(side = BOTTOM)

    ledButton = Button(win, text = "LED ON", font = myFont, command = ledON, height = 2, width =8 )
    ledButton.pack()

    while True:
        win.update_idletasks()
        win.update()

except:
    pass


# mainloop()

'''
