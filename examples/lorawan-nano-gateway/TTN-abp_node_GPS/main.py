from micropyGPS import MicropyGPS
from machine import UART
from network import LoRa
import socket
import binascii
import struct
import time
import config
import tools

DEBUG = config.DEBUG

speed = config.AUTO
update = config.UPDATE[speed] # seconds between update

# Initialize GPS
com = UART(1,pins=(config.TX, config.RX),  baudrate=9600)
my_gps = MicropyGPS()

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

# set the socket port
if DEBUG==1:
    s.bind(config.TTN_FPort_debug)
else:
    s.bing(config.TTN_FPort)

while True:
    if my_gps.fix_stat > 0 and my_gps.latitude[0] > 0:
        pycom.rgbled(0x007f700) # green
    if com.any():
        my_sentence = com.readline()
        for x in my_sentence:
            my_gps.update(chr(x))
        if  DEBUG == 1:
            print('Longitude', my_gps.longitude);
            print('Latitude', my_gps.latitude);
            print('UTC Timestamp:', my_gps.timestamp);
            print('Fix Status:', my_gps.fix_stat);
            print('Altitude:', my_gps.altitude);
            print('Horizontal Dilution of Precision:', my_gps.hdop)
            print('Satellites in Use by Receiver:', my_gps.satellites_in_use)
            print('Speed in km/hour:', int(my_gps.speed[2]))
        gps_speed = int(my_gps.speed[2])
        if (my_gps.fix_stat > 0 and my_gps.latitude[0] > 0) or DEBUG == 1:
            gps_array = tools.convert_latlon(my_gps.latitude[0] + (my_gps.latitude[1] / 60), my_gps.longitude[0] + (my_gps.longitude[1] / 60), my_gps.altitude, my_gps.hdop)
            print(gps_array)
            s.send(gps_array)
            s.settimeout(3.0) # configure a timeout value of 3 seconds
            # get any data received (if any...)
            set_speed = -1
            try:
                data = s.recv(1)
                print(data)
                set_speed = int(data[0])
                print("set_speed = " + str(set_speed))
                if (set_speed > -1 and set_speed < 5):
                    speed = set_speed
                    update = config.UPDATE[speed]
                    print("Update interval set to: " + str(update) + " seconds")
                    print("Speed type set to: " + str(speed))
            except socket.timeout:
                # nothing received
                if (DEBUG == 1):
                    print("No RX downlink data received")
            time.sleep(.5)
            pycom.rgbled(0)
            if (speed == config.AUTO):
                if (gps_speed < config.MAXSPEED[1]):
                    speed_type = config.STAT
                elif (gps_speed < config.MAXSPEED[2]):
                    speed_type = config.WALK
                elif (gps_speed < config.MAXSPEED[3]):
                    speed_type = config.CYCLE
                else:
                    speed_type = config.CAR
                update = config.UPDATE[speed_type]
                print("Update interval set to: " + str(update) + " seconds")
                print("Speed type = " + str(speed))
            time.sleep(update - 8.5) # account for all the other sleep commands
        time.sleep(5)
