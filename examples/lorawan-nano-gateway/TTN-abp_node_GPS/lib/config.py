""" LoPy LoRaWAN Nodeconfiguration options """
from array import array

DEBUG = 1

WIFI_SSID = '<replace with your values>'
WIFI_PASS = '<replace with your values>'
WIFI_IP = '<replace with your values>' # fixed IP
WIFI_SUBNET = '<replace with your values>'
WIFI_GATEWAY = '<replace with your values>'
WIFI_DNS1 = '<replace with your values>'

# TTN
# These you need to replace!
DEV_ADDR = '<replace with your values>'
NWK_SWKEY = '<replace with your values>'
APP_SWKEY = '<replace with your values>'

# set the port, one is used during debugging
# you can filter that port out in the TTN mapper integration
TTN_FPort_debug = 1
TTN_FPort = 2

# CREATE LOG?
LOG = 1
FILENAME = 'log.txt'

# GPS UART connection
TX = "P11"
RX = "P12"

# TIMEZONE / DAYLIGHT SAVING
TIMEZONE = 1
DAYLIGHT = 1

# GPS SPEED variables
AUTO = 0
STAT = 1
WALK = 2
CYCLE = 3
CAR = 4

# update speed in seconds
UPDATE = array('H', [30,30,20,10,10])
MAXSPEED = array('H', [0,1,6,30,150])
