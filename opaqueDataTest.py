#!/usr/bin/python3

import os
import logging
from time import sleep
from pijuice import PiJuice

# for picture date getting
from datetime import datetime


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

# If on battery power, shut down after 3min
data = stat['data']
if data['powerInput'] == "NOT_PRESENT" or "BAD" and data['powerInput5vIo'] == 'NOT_PRESENT' or "BAD":

    print('turning off in 10m, on battery')

    # print data for checking
    print(stat['data'])

	# Write statement to log
    logging.info('Raspberry Pi on battery power. Turning off in 10min - taking picture')

    os.system("/usr/bin/libcamera-still -o /home/opaque/opaqueoceans/image" + str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + ".jpg")

   # Keep Raspberry Pi running - THING TO DO WOULD BE HERE, WOULD TURN OFF AFTER THIS!
    sleep(600)

   # Make sure wakeup_enabled and wakeup_on_charge have the correct values
    pj.rtcAlarm.SetWakeupEnabled(True)
    pj.power.SetWakeUpOnCharge(0)

   # Make sure power to the Raspberry Pi is stopped to not deplete
   # the battery
    pj.power.SetSystemPowerSwitch(0)
    pj.power.SetPowerOff(30)

   # Now turn off the system
    os.system("sudo shutdown -h now")

else:
    # print data for checking
    print(stat['data'])
    print('staying on, mains power')

	# Write statement to log
    logging.info('Raspberry Pi on mains power, not turned off automatically')