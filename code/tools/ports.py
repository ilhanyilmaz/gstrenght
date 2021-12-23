import serial
import serial.tools.list_ports
from itertools import count


def get_available_ports():
    ports = serial.tools.list_ports.comports()
    open_ports = []

    for port in ports:
        try:
            s = serial.Serial(port.name)
            s.close()
            open_ports.append(port.name)
        except (OSError, serial.SerialException):
            pass
    return open_ports

def get_user_port_input():
    open_ports = get_available_ports()
    index = count(1)
    print("Aktif Portlar: \n")
    for port in open_ports:
        print(str(next(index)) + " - " + port)

    while True:
        port_choice = input('\nPort secin: ')
        try:
            return open_ports[int(port_choice)-1]
        except:
            print('hatali giris')

def select_port():
    return get_user_port_input()