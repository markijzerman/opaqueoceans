#!/usr/bin/python3

from pijuice import PiJuice

pj = PiJuice(1,0x14)

getControlStatus = pj.rtcAlarm.GetControlStatus()
getTime = pj.rtcAlarm.GetTime()
getAlarm = pj.rtcAlarm.GetAlarm()

print(getControlStatus)
print(getTime)
print(getAlarm)

print(pj.power.GetWakeUpOnCharge())

# pj.rtcAlarm.SetTime({'data': {'second': 37, 'minute': 28, 'hour': 16, 'weekday': 2, 'day': 7, 'month': 10, 'year': 2019, 'subsecond': 0, 'daylightsaving': 'NONE', 'storeoperation': False}, 'error': 'NO_ERROR'})