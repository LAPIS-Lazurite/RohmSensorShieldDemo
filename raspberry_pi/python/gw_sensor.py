#! /usr/bin/python3

import tkinter as Tk
import tkinter.ttk as ttk 
from tkinter import messagebox
from tkinter import Scale
from tkinter.scrolledtext import ScrolledText
import tkinter.filedialog
from lib.gateway import Gateway
import sys
import time
import struct
import _thread as thread
from datetime import datetime
import urllib.parse
import http.client

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.animation as animation

# Initializing Parameter
LOGO = 'lazurite_mini_b.gif'
BLUE = '#99CCFF'
YELLOW = '#FFCC00'
RED = '#FF00FF'
WHITE = '#FFFFFF'
XSCALL = 180
YSCALL = 28

# GPIO SETTING
INPUT=0
OUTPUT=1
HIZ=2
HIGH = 1
LOW = 0

start_flag = False
LOGO = 'lazurite_mini_b.gif'
mac_menu =("Serial Monitor","Binary Monitor","None")
mac_mode  = 0
SEPARATOR = ","
list_update=False
log_pause=True
sensor_name=[]
sensor_offset=[]
sensor_dim=[]
sensor_count = 0
graph_x=[]
graph_y=[]
def callback(payload,size):
    global log_pause,list_update
    global sensor_name,sensor_dim,sensor_count
    global graph_x,graph_y
    try:
        payload_tmp = payload.decode()
        data = payload_tmp.split(",")
    except:
        return
    if data[0]=="SensorList":
        offset=0
        sensor_count = 0
        for i in range(1,len(data)-1,2):
            print(i,data[i],data[i+1])
            sensor_name.append(data[i])
            sensor_dim.append(int(data[i+1]))
            sensor_offset.append(int(offset))
            offset += int(data[i+1])
            sensor_count += int(data[i+1])
        list_update = True
        for i in range(0,sensor_count):
            graph_y.append([])
        print("Recv SensorList num=",len(sensor_name),"data=",sensor_count)
        return
    elif data[0]=="SensorData":
        if log_pause==False:
            graph_x.append(datetime.now())
            for i in range(0,sensor_count):
                graph_y[i].append(data[i+1])
        return
    elif data[0]=="SensorReset":
        sensor_name=[]
        list_update=False
        print("Recv SensorReset")
        return

gw = Gateway(SEPARATOR,mac_mode,callback)
#gw = Gateway(SEPARATOR,mac_mode)


###### Frame Process

def on_closing():
    if start_flag == False:
#        if messagebox.askokcancel("Quit", "Do you want to quit??"):
#            root.destroy()
         root.destroy()
    else:
        print("please stop gateway")
class SensorGraph(Tk.Frame):
    def __init__(self, master=None):

        Tk.Frame.__init__(self, master)

        self.f_command = Tk.Frame(self)
        self.filename = Tk.StringVar()
        self.filename.set("")

        self.list_sensor = Tk.StringVar()
        self.list_sensor.set("")
        self.c_sensor = ttk.Combobox(self.f_command,textvariable=self.list_sensor, width=20,state="readonly")
        
        self.t_file = Tk.Entry(self.f_command,textvariable=self.filename,width=30, relief=Tk.SUNKEN, bd=2, state=Tk.DISABLED)
        self.b_file = Tk.Button(self.f_command, text='Save as..', command=self.file, state=Tk.NORMAL)
        self.b_start = Tk.Button(self.f_command, text='Logging', command=self.start, state=Tk.DISABLED)
        self.b_stop = Tk.Button(self.f_command, text='Stop', command=self.stop, state=Tk.DISABLED)
        self.c_samples = ttk.Combobox(self.f_command,value=[100,200,500], state="readonly")
        self.c_samples.current(2)

        self.c_sensor.grid(row=0,column=0)
        self.b_file.grid(row=0,column=1)
        self.t_file.grid(row=0,column=2)
        self.b_start.grid(row=0,column=3)
        self.b_stop.grid(row=0,column=4)
        self.c_samples.grid(row=0,column=5)
        self.f_command.pack()
        self.f = Figure(figsize=(5,4), dpi=100)
        self.a = self.f.add_subplot(111)

         # a tk.DrawingArea
        canvas = FigureCanvasTkAgg(self.f, master=self)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( canvas, self )
        toolbar.update()
        canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        ani = animation.FuncAnimation(self.f,self.update,interval=50)
    def start(self):
        global log_pause
        global list_update
        global graph_x, graph_y
        global sensor_name,sensor_offset,sensor_dim

        self.b_start.configure(state=Tk.DISABLED)
        self.b_stop.configure(state=Tk.NORMAL)
        log_pause = False
        return
    def stop(self):
        global log_pause,list_update
        global sensor_count
        global graph_x, graph_y
        global sensor_name,sensor_offset,sensor_dim
        self.b_start.configure(state=Tk.NORMAL)
        self.b_stop.configure(state=Tk.DISABLED)
        log_pause = True
        return
    def file(self):
        return
    def on_key_event(event):
        print('you pressed %s'%event.key)
        key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)

    def update(self,j):
        global log_pause
        global list_update
        global graph_x, graph_y
        global sensor_name,sensor_offset,sensor_dim,sensor_count
        if list_update==True:
            print("Update Sensor List")
            self.c_sensor['value']=sensor_name
            list_update=False
            self.c_sensor.current(0)
            if len(sensor_name) != 0:
                self.b_start.configure(state=Tk.NORMAL)
                self.b_stop.configure(state=Tk.DISABLED)
            else:
                self.b_start.configure(state=Tk.DISABLED)
                self.b_stop.configure(state=Tk.DISABLED)
                graph_x=[]
                graph_y=[]
                log_pause==True
        if log_pause==False:
            self.a.clear()
            num = self.c_sensor.current()
            data_size = len(graph_y[sensor_count-1])
            disp_size = int(self.c_samples.get())
            if disp_size > data_size:
                disp_size = data_size*-1
            else:
                disp_size *= -1
            for i in range(sensor_offset[num],sensor_offset[num]+sensor_dim[num]):
                self.a.plot(graph_x[disp_size:],graph_y[i][disp_size:])
#                print("graph",i,len(graph_x),len(graph_y[i]))
            if 600 < data_size:
                del graph_x[0:data_size - 600]
                for i in range(0,sensor_count):
                    del graph_y[i][0:data_size - 600]
            return
            
        
class GPIO():
    def __init__(self,num):
        self.num = num
        self.config = HIZ
        self.value = LOW
    def set_combo(self,combo):
        self.combo = combo
    def set_scale(self,scale):
        self.scale = scale
    def config_change(self,event):
        self.config = self.combo.current()
        print(self.num,self.config,self.value)
    def  value_change(self,n):
        self.value = n
        print(self.num,self.config,self.value)
        
class Tx(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.tx_frame = Tk.Frame(self)

        self.gpio = []
        for i in range(0,20):
            self.gpio.append(GPIO(i))
            # GPIO LABEL
            self.gpio_hdr = Tk.Label(self.tx_frame,text="PORT%02d"%i, anchor=Tk.W)

            # GPIO Configure
            self.c_gpio_config = ttk.Combobox(self.tx_frame,value=["INPUT","OUTPUT","HIZ"], state="readonly")
            self.c_gpio_config.current(HIZ)
            self.c_gpio_config.bind("<<ComboboxSelected>>",self.gpio[i].config_change)
            self.gpio[i].set_combo(self.c_gpio_config)

            # GPIO scaler
            self.s_gpio_value = Scale(self.tx_frame,orient = 'h',showvalue = 0,from_ = 0, to = 1,command = self.gpio[i].value_change)
            self.gpio[i].set_scale(self.s_gpio_value)

            self.gpio_hdr.grid(row=i, column=0, padx=5, pady=0)
            self.c_gpio_config.grid(row=i, column=1, padx=5, pady=0)
            self.s_gpio_value.grid(row=i, column=2, padx=5, pady=0)
        self.tx_frame.pack()

###### Setting & Receive TAB GUI ######
class Rx(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
#### COMMAND DISPLAY
        self.panid= Tk.IntVar()
        self.panid=0xABCD
        self.PanidDisp= Tk.StringVar()
        self.PanidDisp.set(hex(self.panid))

        self.row_offset = 0

# DISPLAY LOGO
        f_command = Tk.Frame(self,  bd=4)
        self.image= Tk.PhotoImage(file=LOGO)
        self.logoBackGround=Tk.Label(f_command, image=self.image, bg='gray', relief=Tk.RIDGE, anchor=Tk.W)
        f_cb = Tk.Frame(self,bd=4)

# DISPLAY Channel
        self.ch =36
        self.chNumberDisp = Tk.IntVar()
        self.chNumberDisp.set(self.ch)

        self.l_ch = Tk.Label(f_command,text="Ch", relief=Tk.RIDGE, anchor=Tk.W)
        self.t_ch = Tk.Entry(f_command,textvariable=self.chNumberDisp,width=10, relief=Tk.SUNKEN, bd=2, state=Tk.NORMAL)
        
        self.b_chIncButton = Tk.Button(f_command, font=('Helvetica', '6'), text='+', command=self.chInc)
        self.b_chDecButton = Tk.Button(f_command, font=('Helvetica', '6'), text='-', command=self.chDec)

# DISPLAY Power
        self.pwr = (1,20)
        
        self.l_pwr = Tk.Label(f_command,text="Pwr", relief=Tk.RIDGE, anchor=Tk.W)
        self.b_pwr = ttk.Combobox(f_command,value=self.pwr, width=10,state="readonly")
        self.b_pwr.current(1)
        
# DISPLAY Rate
        self.rate = (50,100)

        self.l_rate = Tk.Label(f_command,text="Rate", relief=Tk.RIDGE, anchor=Tk.W)
        self.b_rate = ttk.Combobox(f_command,value=self.rate, width=10,state="readonly")
        self.b_rate.current(1)

# DISPLAY PANID
        self.l_panid = Tk.Label(f_command,text="PANID", relief=Tk.RIDGE, anchor=Tk.W)
        self.t_panid = Tk.Entry(f_command,textvariable=self.PanidDisp,width=10, relief=Tk.SUNKEN, bd=2, state=Tk.NORMAL)

# DISPLAY Start/Stop Button         
        self.b_start = Tk.Button(f_command, text='Start', command=self.Start)
        self.b_stop = Tk.Button(f_command, text='Stop', command=self.Stop, state=Tk.DISABLED)


## Option check buttom
        self.ign = Tk.BooleanVar()
        self.c_ign = Tk.Checkbutton(f_command,text="Ignore address",variable=self.ign)

# DISPLAY display mode
        global mac_menu
        global mac_combobox
        global mac_mode

        mac_combobox=ttk.Combobox(f_command,value=mac_menu,width=20,state="readonly")
        mac_combobox.current(mac_mode)
        mac_combobox.bind("<<ComboboxSelected>>",self.dispMode)
        
# DISPLAY save log buttom
        self.b_savelog=Tk.Button(f_command, text='SAVE', command=self.Save, state=Tk.NORMAL)
        self.b_clearlog=Tk.Button(f_command, text='CLEAR LOG', command=self.Clear, state=Tk.NORMAL)

## Command Frame Location
        self.logoBackGround.grid(row=0,column=0)
        self.b_start.grid(row=0, column=4)
        self.b_stop.grid(row=0, column=5)

        self.l_ch.grid(row=2,column=0,sticky=Tk.W + Tk.E,pady=10)
        self.t_ch.grid(row=2,column=1,padx=20,sticky=Tk.W)
        self.b_chIncButton.grid(row=2, column=4, sticky=Tk.W + Tk.E + Tk.S)
        self.b_chDecButton.grid(row=2, column=5, sticky=Tk.W + Tk.E + Tk.S)

        self.l_pwr.grid(row=4,column=0,sticky=Tk.W + Tk.E,pady=10)
        self.b_pwr.grid(row=4,column=1,padx=20,sticky=Tk.W)

        self.l_rate.grid(row=5,column=0,sticky=Tk.W + Tk.E,pady=10)
        self.b_rate.grid(row=5,column=1,padx=20,sticky=Tk.W)

        self.l_panid.grid(row=6,column=0,sticky=Tk.W + Tk.E,pady=10)
        self.t_panid.grid(row=6,column=1,padx=20,sticky=Tk.W)

        self.c_ign.grid(row=0,column=6,sticky=Tk.W + Tk.E,padx=20)
        mac_combobox.grid(row=5,column=6,padx=20)
        self.b_savelog.grid(row=6,column=6,padx=20)
        self.b_clearlog.grid(row=6,column=7,padx=20)

## LOG WINDOW
        global XSCALL
        global YSCALL
        f_log = Tk.Frame(self)
#        self.logText = Tk.StringVar()
#        self.logText.set("")
        self.s_logtext=ScrolledText(f_log,width=XSCALL, height=YSCALL)
#        self.s_logtext.grid(sticky=Tk.W+Tk.E,)
        self.s_logtext.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.s_logtext.write = self.write
        sys.stdout = self.s_logtext

## FRAME Location
        f_command.pack()
        f_log.pack()

    def write(self,str):
        self.s_logtext.insert(Tk.END,str)
        time.sleep(0.001)
        self.s_logtext.yview_scroll(str.count("\n") + 1, "units")

    def Start(self):
        global start_flag

        ## update parameters
        self.ch = self.chNumberDisp.get()
        self.pwr = int(self.b_pwr.get())
        self.rate = int(self.b_rate.get())
        self.panid = int(self.PanidDisp.get(),0)

        ## parameter check
        if self.ch < 24 or self.ch > 61:
            print("ch number error")
            return

        if self.pwr != 1 and self.pwr != 20:
            print("power error =",self.pwr)
            return

        if self.rate != 50 and self.rate != 100:
            print("rate error=",self.rate)
            return

        if self.panid <= 0 or self.panid > 0xffff:
            print("PANID error")
            return
        
        ## Start Gateway
        self.b_start.configure(state=Tk.DISABLED)
        self.b_stop.configure(state=Tk.NORMAL)
        self.b_chIncButton.configure(state=Tk.DISABLED)
        self.b_chIncButton.configure(state=Tk.DISABLED)
        self.logoBackGround.configure(bg=BLUE)
        self.b_savelog.configure(state=Tk.DISABLED)
        start_flag = True
        self.init_gateway()

        
    def Stop(self):
        global start_flag
        self.b_start.configure(state=Tk.NORMAL)
        self.b_stop.configure(state=Tk.DISABLED)
        self.b_chIncButton.configure(state=Tk.NORMAL)
        self.b_chIncButton.configure(state=Tk.NORMAL)
        self.logoBackGround.configure(bg='gray')
        self.b_savelog.configure(state=Tk.NORMAL)
        gw.stop()
        start_flag = False

        
    def chInc(self):
        self.ch = self.chNumberDisp.get()
        if self.ch < 61 and self.ch >= 24:
            self.ch += 1
        elif self.ch < 24:
            self.ch = 24
        else:
            self.ch = 61
        self.chSet()
            
    def chDec(self):
        self.ch = self.chNumberDisp.get()
        if self.ch <= 61 and self.ch > 24:
            self.ch -= 1
        elif self.ch > 61:
            self.ch = 61
        else:
            self.ch = 24
        self.chSet()
        
    def chSet(self):
        self.chNumberDisp.set(self.ch)

    def dispMode(self,event):
        gw.setDispMode(mac_combobox.current())

    def Clear(self):
        self.s_logtext.delete(1.0,Tk.END)

    def Save(self):
        filename = Tk.filedialog.asksaveasfile(filetypes = [('Log Files', ('.log'))])
        if filename != "":
            logfile = open(filename.name,mode = 'w')
            log_data = self.s_logtext.get(1.0,Tk.END)
            logfile.write(log_data)
            logfile.close()
        return
        
    def init_gateway(self):
        if self.ign.get():
            self.mode = 1
        else:
            self.mode = 0
        gw.start(self.ch,self.pwr,self.rate,self.panid,self.mode)
        

class Frame(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)

        self.note = ttk.Notebook(self)
        self.master.title('Lazurite Gateway')
        self.tab_a = Rx(self.note)
#        self.tab_b = Tx(self.note)
        self.tab_c = SensorGraph(self.note)
        self.note.add(self.tab_a, text="Setting & Receive")
#        self.note.add(self.tab_b, text="Transfer")
        self.note.add(self.tab_c, text="Sensor Graph")
        self.note.pack()

if __name__ == '__main__':
    root = Tk.Tk()
    f = Frame(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    f.pack()
    f.mainloop()
