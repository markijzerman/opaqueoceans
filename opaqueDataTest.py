#!/usr/bin/python3

import subprocess, os
import atexit
import logging
from time import sleep
from pijuice import PiJuice

# VALUES
time = 20

# for internet connection check
import urllib.request

# for picture date getting 
from datetime import datetime

# for checkin internet connection
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False
    
# for checking if user is logged on
def checkForUser():
    piUserList = subprocess.check_output('users', shell=True).rstrip()
    if piUserList:
        logging.info('user is logged in, staying on!')
        print('user is logged on, staying on')
        return True
    else:
        logging.info('no users logged in, turning off...')
        return False
    
# called when program exits
def exit_handler():
    # Make sure wakeup_enabled and wakeup_on_charge have the correct values
    pj.rtcAlarm.SetWakeupEnabled(True)
    pj.power.SetWakeUpOnCharge(0)

logging.basicConfig(
	filename = '/home/opaque/opaqueoceans/pistatus.log',
	level = logging.DEBUG,
	format = '%(asctime)s %(message)s',
	datefmt = '%d/%m/%Y %H:%M:%S')

pj = PiJuice(1,0x14)

pjOK = False
while pjOK == False:
   stat = pj.status.GetStatus()
   if stat['error'] == 'NO_ERROR':
      pjOK = True
   else:
      sleep(0.1)



# print data for checking
print(stat['data'])

# Write statement to log
logging.info('Hello! Raspberry Pi on battery power. Taking picture!')

curDate = str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
os.system("/usr/bin/libcamera-still -o /home/opaque/opaqueoceans/images/image" + curDate + ".jpg")

# if internet, upload image
# !! CHANGE THIS TO UPLOAD ANY THAT HAVE NOT BEEN UPLOADED !!
if connect() == True:
    print('Internet is connected! Uploading image!')
    os.system("/home/opaque/opaqueoceans/dropbox_uploader.sh upload /home/opaque/opaqueoceans/images/image" + curDate + ".jpg /")
else:
    print('no internet, uploading later')

# check if there is a user logged on, if so stay on, if not, turn off
# Keep Raspberry Pi running - THING TO DO WOULD BE HERE, WOULD TURN OFF AFTER THIS!
if checkForUser() == False:
    sleep(time)
    
    # Make sure wakeup_enabled and wakeup_on_charge have the correct values
    pj.rtcAlarm.SetWakeupEnabled(True)
    pj.power.SetWakeUpOnCharge(0)

    # Make sure power to the Raspberry Pi is stopped to not deplete
    # the battery
    pj.power.SetSystemPowerSwitch(0)
    pj.power.SetPowerOff(30)

    logging.info('Bye! shutting down now as time has elapsed')

    # Now turn off the system
    os.system("sudo shutdown -h now")

atexit.register(exit_handler)