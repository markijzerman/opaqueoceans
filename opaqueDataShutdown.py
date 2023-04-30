#!/usr/bin/python3

import os
import logging
from pijuice import PiJuice

logging.basicConfig(
	filename = '/home/opaque/opaqueoceans/pistatus.log',
	level = logging.DEBUG,
	format = '%(asctime)s %(message)s',
	datefmt = '%d/%m/%Y %H:%M:%S')

pj = PiJuice(1,0x14)

# Set wakeup_enabled and wakeup_on_charge just to be sure
pj.rtcAlarm.SetWakeupEnabled(True)

# The Raspberry Pi should wake up even when there is no battery, i.e. a
# battery percentage of 0
# DISABLED FOR NOW TO MAKE SURE THIS IS NOT THE REASON FOR IT FAILING
pj.power.SetWakeUpOnCharge(0)
pj.rtcAlarm.SetAlarm({'minute_period': 60})

# Write statement to log
logging.info('Raspberry Pi battery running low - shutting down')

# Show custom script is run by blinking the user LED red 10x
pj.status.SetLedBlink('D2', 10, [200,0,0], 50, [0, 0, 0], 50)

# Now shut down
os.system("sudo shutdown -P +1")