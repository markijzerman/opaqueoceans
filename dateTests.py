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