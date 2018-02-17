from micropyGPS import MicropyGPS
from machine import UART
from machine import SD
from machine import RTC
import os
import time
import config
import array
from network import WLAN
from network import LoRa
import socket
import binascii
import struct

def connect_wifi():
    wlan = WLAN()
    wlan.init(mode=WLAN.STA)
    wlan.ifconfig(config=(config.WIFI_IP, config.WIFI_SUBNET, config.WIFI_GATEWAY, config.WIFI_DNS1))   
    wlan.connect(config.WIFI_SSID, auth=(WLAN.WPA2, config.WIFI_PASS), timeout=5000)    
    return wlan.ifconfig()

def mount_sd():
    sd = SD()
    os.mount(sd, '/sd/')
    return os.listdir('/sd')
  
def start_GPS():    
    com = UART(1,pins=("P11","P12"),  baudrate=9600) 
    my_gps = MicropyGPS()
    if config.LOG == 1:
        mount_sd()
        my_gps.start_logging('/sd/log.txt')
        my_gps.write_log('Restarted logging')

    while True:
        if com.any():
            my_sentence = com.readline()
            for x in my_sentence:
                my_gps.update(chr(x))
            print('Latitude: ' + my_gps.latitude_string() + ' Longitude: ' + my_gps.longitude_string() + ' Altitude: ' + str(my_gps.altitude))
            print('Lat / Lon: ' + str(my_gps.latitude[0] + (my_gps.latitude[1] / 60)) + ', ' + str(my_gps.longitude[0] + (my_gps.longitude[1] / 60)))


def convert_latlon(latitude, longitude, altitude, hdop):
# latitude = -7.005941
# longitude = -68.1192

    lat = int((latitude + 90)*10000)
    lon = int((longitude + 180)*10000)
    alt = int((altitude) * 10)
    lhdop = int((hdop) * 10)

    coords = array.array('B', [0,0,0,0,0,0,0,0,0])
    coords[0] = lat
    coords[1] = (lat >> 8)
    coords[2] = (lat >> 16)

    coords[3] = lon
    coords[4] = (lon >> 8)
    coords[5] = (lon >> 16)

    coords[6] = alt
    coords[7] = (alt >> 8)
    coords[8] = lhdop

    return coords
    
    
def get_GPS_values():    
    com = UART(1,pins=(config.TX, config.RX),  baudrate=9600) 
    my_gps = MicropyGPS()
    time.sleep(2)
    if com.any():
        my_sentence = com.readline()
        for x in my_sentence:
            my_gps.update(chr(x))
        gps_values = str(my_gps.latitude[0] + (my_gps.latitude[1] / 60)) + ',' + str(my_gps.longitude[0] + (my_gps.longitude[1] / 60))
        return gps_values

def get_GPS_array():    
    com = UART(1,pins=(config.TX, config.RX),  baudrate=9600) 
    my_gps = MicropyGPS()
    time.sleep(2)
    if com.any():
        my_sentence = com.readline()
        for x in my_sentence:
            my_gps.update(chr(x)) 
        gps_array = convert_latlon(my_gps.latitude[0] + (my_gps.latitude[1] / 60), my_gps.longitude[0] + (my_gps.longitude[1] / 60))
        return gps_array
        
        
def set_date_time():    
    com = UART(1,pins=(config.TX, config.RX),  baudrate=9600) 
    my_gps = MicropyGPS()
    time.sleep(2)
    if com.any():
        my_sentence = com.readline()
        for x in my_sentence:
            my_gps.update(chr(x)) 
        date = my_gps.date
        timestamp = my_gps.timestamp
        hour = timestamp[0]
        hour = hour + config.TIMEZONE
        if config.DAYLIGHT == 1:
            hour = hour + 1
        rtc = RTC(datetime=(int(date[2])+2000, int(date[1]), int(date[0]), int(timestamp[0]), int(timestamp[1]), int(timestamp[2]), 0, None)) 
        return rtc      
        
def send_LORA(value):
    # Initialize LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN)

    # create an ABP authentication params
    dev_addr = struct.unpack(">l", binascii.unhexlify(config.DEV_ADDR.replace(' ','')))[0]
    nwk_swkey = binascii.unhexlify(config.NWK_SWKEY.replace(' ',''))
    app_swkey = binascii.unhexlify(config.APP_SWKEY.replace(' ',''))

    # join a network using ABP (Activation By Personalization)
    lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

    # remove all the non-default channels
    for i in range(3, 16):
        lora.remove_channel(i)

    # set the 3 default channels to the same frequency
    lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
    lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
    lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)

    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

    # make the socket blocking
    s.setblocking(False)        

    s.send(bytes(value))
