# encoding:utf-8
#https://pyserial.readthedocs.io/en/latest/shortintro.html#eol
import sys
import serial
from serial import Serial
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, TextBox
import matplotlib.text as text

import csv
import time
from itertools import count
import threading
from tools.ports import select_port
from tools.settings import DEBUG, PORT_NAME, BAUD_RATE, TIMESTAMP_FORMAT, MIN_FORCE, PLOT_STYLE, X_LABEL, Y_LABEL
from datetime import datetime

reading_active = False
current_reading_starting_index = 0
data_name = "default"
x_vals = []
y_vals = []
try_maxes =[]

index = count()

ser = None
read_data = True
x = None
y = None
fig, ax=plt.subplots()
fig.subplots_adjust(bottom=0.2)
text_box = None
axbox = fig.add_axes([0.1, 0.01, 0.3, 0.05])
text_box = TextBox(axbox, 'Isim', textalignment='center')
buttonbox = fig.add_axes([0.50, 0.01, 0.14, 0.05])
btn_stop = Button(buttonbox, 'Kaydet')
buttonbox2 = fig.add_axes([0.65, 0.01, 0.14, 0.05])
btn_new = Button(buttonbox2, 'Yeni Kayıt')
buttonbox3 = fig.add_axes([0.80, 0.01, 0.14, 0.05])
btn_clear = Button(buttonbox3, 'Temizle')

#btn_stop = Button(buttonbox, 'Kaydet')

warning = ""

def reset_values():
    global x_vals, y_vals, try_maxes,current_reading_starting_index
    x_vals=[]
    y_vals=[]
    try_maxes=[]
    current_reading_starting_index=0
    #input_name()

def get_connection():
    com_port = PORT_NAME
    while True:
        ser = Serial()
        ser.baudrate = BAUD_RATE # TODO: read from settings.txt
        ser.port = com_port  # TODO: read from settings.txt
        try:
            ser.open()
            return ser
        except:
            com_port = select_port()    

def get_timestamp():
    return datetime.now().strftime(TIMESTAMP_FORMAT)

def save_graph(timestamp=None):
    if timestamp == None:
        timestamp = get_timestamp()
    plt.savefig("../graph/" + data_name + "_" + timestamp + '.png')

def plot_graph(x_values, y_values):
    ax.cla()
    plt.style.use(PLOT_STYLE)
    legend = data_name
    if len(y_values)>0:
         legend = legend+ "(Max: " + str(max(y_values)) +")"
    ax.plot(x_values, y_values, label=legend)
    ax.set_ylabel(Y_LABEL)
    ax.set_xlabel(X_LABEL + '\n ' + warning)
    ax.legend(loc='upper center')
    #plt.tight_layout()
    plt.show()

def load_from_file():
    data = pd.read_csv("../data/" + data_name + '.csv')
    print("Max: " + str(max(data['y_value'])) )
    plot_graph(data['x_value'],data['y_value'])
    
def write_to_file(timestamp=None):
    if timestamp == None:
        timestamp = get_timestamp()
    fieldnames = ['x_value', 'y_value']
    with open('../data/' + data_name + "_" + timestamp + '.csv', 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for i in range(len(y_vals)):

            info = {
                'x_value': x_vals[i],
                'y_value': y_vals[i]
            }

            csv_writer.writerow(info)
def log_current_reading():
    global reading_active, current_reading_starting_index, warning, try_maxes
    reading_active= False
    current_max = max(y_vals[current_reading_starting_index:])
    try_maxes.append(current_max)
    warning = str(try_maxes)
    #warning = "current max: " + str(current_max)
    current_reading_starting_index=len(x_vals)

def get_data():
    global ser, reading_active
    while read_data:
        try:
            data = ser.readline(20) # try empty or different values
            val = float(data)
            if val < MIN_FORCE:
                if reading_active:
                    log_current_reading()
                continue
            elif reading_active == False:
                reading_active = True
            x_vals.append(next(index)/40.0)
            y_vals.append(float(data))
        except TypeError as e:
            break
        except:
            data_str = str(data)
            pos = data_str.find('Max kg')
            if pos>0:
                data_str = data_str[pos+8:]
                print('Max value is: '+ data_str[:data_str.find('\\')])
                return
            else:
                print(data)

def start_reading():
    global read_data, y
    print("start_reading event triggered")
    read_data=True

    try:
        ser.write(b'q')
        y = threading.Thread(target=get_data)
        y.start()
    except:
        print("Couldn't send command to device")

def stop_reading():
    global read_data
    print("stop_reading event triggered")
    read_data=False
    try:
        ser.write(b'w')
    except:
        print("Couldn't send command to device")

def name_change(expression):
    global data_name, cid
    print("name_change event triggered")
    if expression:
        data_name = expression
        #text_box.on_submit(None)
        axbox.set_visible(False)
        buttonbox.set_visible(True)
        buttonbox2.set_visible(True)
        buttonbox3.set_visible(True)
        #reset_values()
        start_reading()

def add_textbox():
    axbox.set_visible(True)
    buttonbox.set_visible(False)
    buttonbox2.set_visible(False)
    buttonbox3.set_visible(False)

def on_clear(event):
    reset_values()

def on_stop_reading(event):
    global warning
    #print(str(event))
    stop_reading()
    timestamp = get_timestamp()
    write_to_file(timestamp)
    save_graph(timestamp)
    warning = "Grafik kaydedildi!"

def on_new_reading(event):
    global warning
    #print(str(event))
    #reset_values()
    add_textbox()

def on_close(event):
    global read_data
    read_data = False
    #plt.close()
    try:
        ser.close()
    except:
        pass

def animate(i):
    plot_graph(x_vals, y_vals)

def debug_animate(i):
    data = pd.read_csv('data.csv')
    x = data['x_value']
    y1 = data['y_value']

    #x_vals.append(next(index))
    #y_vals.append(random.randint(0, 5))

    plt.cla()
    plt.style.use(PLOT_STYLE)
    #plt.plot(x_vals, y_vals, label='Maximum')
    plt.plot(x, y1, label=str(data_name))
    plt.annotate('100', (5, 5), (5, 1), ha='center', va='center', arrowprops = {'arrowstyle':"->", 'color':'C1'})
    plt.legend(loc='upper center')
    plt.tight_layout()

#x = threading.Thread(target=get_input)
#x.start()

if DEBUG:
    ani = FuncAnimation(plt.gcf(), debug_animate, interval=100) #500ms

else:
    ser = get_connection()
    ani = FuncAnimation(plt.gcf(), animate, interval=100) #500ms


btn_stop.on_clicked(on_stop_reading)
btn_new.on_clicked(on_new_reading)
btn_clear.on_clicked(on_clear)
text_box.on_submit(name_change)
add_textbox()

fig.canvas.mpl_connect('close_event', on_close)
#plt.tight_layout()
plt.show()


