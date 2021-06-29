
import serial
import time
import screen_brightness_control as sbc
import math
from threading import Thread
from tkinter import Tk, Button,  Label, Frame, ttk, DoubleVar, messagebox
import csv

class GUI(Frame):
    def create_widgets(self):
        self.Label1 = Label(self,text = "Brightness : ")
        self.Label1.grid(row = 0, column = 0, sticky = "w")
        self.Label2 = Label(self,text = "Distance :")
        self.Label2.grid(row = 1, column = 0, sticky = "w")
        self.Label3 = Label(self,text = "Ambient Brightness :")
        self.Label3.grid(row = 2, column = 0, sticky = "w")
        self.Label4 = Label(self,text = "Brightness Difference : ")
        self.Label4.grid(row = 3, column = 0, sticky="w")
        self.Label5 = Label(self,text = "Time Lapsed : ")
        self.Label5.grid(row = 4, column = 0, sticky="w")
        self.board = None
        self.current_value = DoubleVar()
        self.current_value.set(50.0)
        self.slider_label = ttk.Label(
            self,
            text='Slider:'
        )

        self.slider_label.grid(
            column=0,
            row=6,
            sticky='w'
        )

        #  slider
        self.slider = ttk.Scale(
            self,
            from_=0,
            to=100,
            orient='horizontal',  # vertical
            command=self.slider_changed,
            variable=self.current_value,
            value = 50.0
        )

        self.slider.grid(
            column=1,
            row=6,
            sticky='we'
        )

        # current value label
        self.current_value_label = ttk.Label(
            self,
            text='Current Value:'
        )

        self.current_value_label.grid(
            row=7,
            columnspan=2,
            sticky='n',
            ipadx=10,
            ipady=10
        )

        # value label
        self.value_label = ttk.Label(
            self,
            text=self.get_current_value()
        )
        self.value_label.grid(
            row=8,
            columnspan=2,
            sticky='n'
        )
        self.count = -1
        self.run = False
        self.set_val = 0
        self.saved_data = []
        self.control_flag = True
        self.save_flag = True
        self.start = Button(self, text='Start',width=25, command=lambda: Thread(target=self.Start).start())
        self.stop = Button(self, text='Stop', width=25, state='disabled', command=self.Stop)
        self.reset = Button(self, text='Reset&Save',width=25, state='disabled', command = self.Reset)
        self.control = Button(self, text="Brighness Ctrl : ON", width=25, state='normal', command=self.enable_control)
        self.save = Button(self, text="Save Data: ON", width=25, state='normal', command=self.enable_save)
        self.start.grid(row = 5, column = 0)
        self.stop.grid(row = 5, column = 1)
        self.reset.grid(row = 5, column = 2)
        self.control.grid(row=5,column=3)
        self.save.grid(row=5,column=4)
    
    def enable_control(self):
        if self.control_flag :
            self.control['text'] = "Brighness Ctrl : OFF"
            self.control_flag = False
        else :
            self.control['text'] = "Brighness Ctrl : ON"
            self.control_flag = True

    def enable_save(self):
        if self.save_flag :
            self.save['text'] = "Save Data: OFF"
            self.save_flag = False
        else :
            self.save['text'] = "Save Data: ON"
            self.save_flag = True

    def get_current_value(self):
        return self.current_value.get()


    def slider_changed(self,event):
        self.value_label.configure(text='{: .2f}'.format(self.get_current_value()))
        brightness = int(self.get_current_value())
        sbc.set_brightness(brightness)
    
    def time_convert(self):
        mins = self.count // 60
        sec = self.count % 60
        hours = mins // 60
        mins = mins % 60
        text = "Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec)
        return text

    def brightness_control(self,LDR_r,Length,diff) :
        if Length > 40 :
            Length = 40
        coef= 7.0649 - 0.2207*Length 
        grad = 2.1536 - 0.0343*Length
        brightness_diff = (diff-coef)/grad
        if brightness_diff < 0 :
            brightness_diff = 0
        if LDR_r<self.set_val-4 :
            cur_brightness = sbc.get_brightness()
            brightness = int(cur_brightness+brightness_diff)
            if brightness > 100 :
                brightness = 100
            sbc.set_brightness(brightness)
        elif LDR_r > self.set_val+4 and LDR_r!=0 :
            cur_brightness = sbc.get_brightness()
            brightness = int(cur_brightness-brightness_diff)
            if brightness < 0 :
                brightness = 0
            sbc.set_brightness(brightness)

    def var_name(self):
        while self.run:
            try :
                ser = str(self.board.readline())
                data =  ser.split(",")
                LDR_r = float(data[1])
                Length = float(data[2])
                Ambient_r = float(data[3])
                diff = math.fabs(LDR_r - self.set_val)
                if self.count <= 3:
                    show1 = "Starting"
                    show2 = "Starting"
                    show3 = "Starting"
                    show4 = "Starting"
                    show5 = "Starting"
                    self.set_val += LDR_r
                    if self.count == 3:
                        self.set_val = self.set_val/5
                else:
                    show1 = "Brightness : %f lux" % LDR_r
                    show2 = "Distance : %f cm" % Length
                    show3 = "Ambient Brightness : %f lux" % Ambient_r
                    show4 = "Brightness Difference : %f " % diff
                    show5 = self.time_convert()
                self.Label1['text'] = show1
                self.Label2['text'] = show2
                self.Label3['text'] = show3
                self.Label4['text'] = show4
                self.Label5['text'] = show5
                #Increment the count after
                #every 1 second
                if self.count>3 and self.control_flag and self.save_flag:
                    self.brightness_control(LDR_r,Length,diff)
                    data = [LDR_r,Length,Ambient_r]
                    self.saved_data.append(data)
                elif self.count>3 and self.control_flag and not(self.save_flag):
                    self.brightness_control(LDR_r,Length,diff)
                elif not(self.control_flag) and self.save_flag :
                    data = [LDR_r,Length,Ambient_r]
                    self.saved_data.append(data)
                self.count += 1
            except :
                self.run=False



    # While stopped
    def Stop(self):
        self.slider['state']='normal'
        self.start['state'] = 'normal'
        self.stop['state'] = 'disabled'
        self.reset['state'] = 'normal'
        self.control['state'] = 'normal'
        self.save['state'] = 'normal'
        self.run = False
        if self.board != None :
            self.board.close()

    def Write_data(self):
        header = ["Brightness","Distance","Ambient Brightness"]
        with open ("Controlled_Data.csv", 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(self.saved_data)

    # For Reset
    def Reset(self):
        self.count = -1
        self.set_val = 0
        self.reset['state'] = 'disabled'
        self.Label1['text'] = "Distance : "
        self.Label2['text'] = "Ambient Brightness : "
        self.Label3['text'] = "Brightness Difference : "
        self.Label4['text'] = "Brightness Difference : "
        self.Label5['text'] = "Time Lapsed : "
        if self.save_flag :
            self.Write_data()
            self.saved_data.clear()




    # While Running
    def Start(self):
        try :
            self.board = serial.Serial('COM5', 9600, timeout = 1)
            self.run = True
            self.start['state'] = 'disabled'
            self.stop['state'] = 'normal'
            self.reset['state'] = 'disabled'
            self.slider['state'] = 'disabled'
            self.control['state'] = 'disabled'
            self.save['state'] = 'disabled'
            self.var_name()
        except :
            messagebox.showerror("Error", "Device Tidak Terdeteksi !!")
            self.start['state'] = 'normal'
            self.stop['state'] = 'disabled'
            self.reset['state'] = 'disabled'
            self.slider['state'] = 'normal'
            pass
    
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.create_widgets()
        self.grid()

root = Tk()
app = GUI(master = root)
app.mainloop()










    






