# encoding:utf-8
#https://pyserial.readthedocs.io/en/latest/shortintro.html#eol

import serial
from serial import Serial
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import csv
import time
from itertools import count
import threading
from tools.ports import select_port
from tools.settings import PORT_NAME, BAUD_RATE, TIMESTAMP_FORMAT, MIN_FORCE
from datetime import datetime

data_name = input("Isim girin: ")
x_vals = []
y_vals = []
index = count()
read_data = True

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
    plt.savefig("../graph/" + data_name + timestamp + '.png')

def plot_graph(x_values, y_values):
    plt.cla()
    legend = data_name
    if len(y_values)>0:
         legend = legend+ "(Max: " + str(max(y_values)) +")"
    plt.plot(x_values, y_values, label=legend)
    
    plt.legend(loc='upper center')
    plt.tight_layout()
    plt.show()

def load_from_file():
    data = pd.read_csv("../data/"+data_name + '.csv')
    print("Max: " + str(max(data['y_value'])) )
    plot_graph(data['x_value'],data['y_value'])
    
def write_to_file(timestamp=None):
    if timestamp == None:
        timestamp = get_timestamp()
    fieldnames = ['x_value', 'y_value']
    with open('../data/' + data_name + timestamp + '.csv', 'w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for i in range(len(y_vals)):

            info = {
                'x_value': x_vals[i],
                'y_value': y_vals[i]
            }

            csv_writer.writerow(info)
            
def get_data():
    while read_data:
        data = ser.readline(20) # try empty or different values
        try:
            val = float(data)
            if val < MIN_FORCE:
                continue
            x_vals.append(next(index)/40.0)
            y_vals.append(float(data))
        except:
            data_str = str(data)
            pos = data_str.find('Max kg')
            if pos>0:
                data_str = data_str[pos+8:]
                print('Max value is: '+ data_str[:data_str.find('\\')])
                return
            else:
                print(data)
        

def print_commands():
    print(" ")
    print("Komutlar:")
    print(" ")
    print("  [q] : Veri okumaya basla")
    print("  [w] : Veri okumayi durdur")
    print("  [s] : Verileri kaydet")
    print("  [l] : Verileri goster")
    print("  [g] : Grafik kaydet")
    print("  [x] : Cikis")
    print(" ")


def get_input():
    timestamp = get_timestamp()

    while True:
        print_commands()
        val = input("Komut girin: ")
        print(val)
        if val == 'q':
            read_data=True
            try:
                ser.write(b'q')
                y = threading.Thread(target=get_data)
                y.start()
            except:
                pass

        elif val == 'w':
            read_data=False
            timestamp = get_timestamp()
            try:
                ser.write(b'w')
            except:
                pass
        elif val == 's':
            write_to_file(timestamp)
        elif val == 'l':
            read_data = False
            load_from_file()
        elif val == 'g':
            save_graph(timestamp)
        elif val == 'x':
            plt.close()
            try:
                ser.close()
            except:
                pass
            break
        else:
            print('Komut bulunamadi: ' + val)

def animate(i):
    plot_graph(x_vals, y_vals)
    

ser = get_connection()

x = threading.Thread(target=get_input)
x.start()

ani = FuncAnimation(plt.gcf(), animate, interval=100) #500ms
plt.tight_layout()
plt.show()


