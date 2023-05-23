#!/usr/bin/python3

import subprocess, os
import atexit
import logging
from time import sleep
from pijuice import PiJuice

import typing as tp

import glob
import json

# VALUES
time = 20

# for internet connection check
import urllib.request

# for picture date getting 
from datetime import datetime, timedelta

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line.startswith('Serial'):
        cpuserial = line.split(":")[1].strip()
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

def get_uuid() -> str:
    try:
        serial = getserial()

        with open("config.json") as f:
            names = json.load(f)
            if isinstance(names, dict):
                return names["device_name"][serial]
            else:
                logging.warn(f"Failed to get unique name from serial, just using serial.")
                return serial
    except:
        pass

# for checkin internet connection
def connect(host='http://google.com'):
    try:
        if not os.system("curl google.com --fail-early -s -I -o /dev/null"):
            return True
        
        return False
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

def get_alarm_config() -> dict:
    config_path = "/home/opaque/opaqueoceans/config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            try:
                return json.load(f)['alarm_config']
            except Exception as e:
                logging.warning(f"Failed to load alarm config: {e}")
    
    return None

def get_hour_minute_tuple_from_str(time: str) -> tp.Tuple[int, int]:
    times = time.split(":")
    return (int(times[0]), int(times[1]))

def get_time_dt_obj_from_time_str(time: str) -> timedelta:
    times = get_hour_minute_tuple_from_str(time)
    return timedelta(hours=times[0], minutes=times[1])

def get_hour_minute_tuple_from_time_dt(time: timedelta) -> tp.Tuple[int, int]:
    hour = (time.seconds // 3600) % 24
    minute = (time.seconds // 60) % 60
    return (hour, minute)

# Week starts on sunday because US of A, range is 1-7
def get_weekday_from_period(period: int, current_weekday: int) -> int:
    return ((current_weekday - 1 + period) % 7) + 1


def get_next_periodic_alarm_time(cfg: dict, time: timedelta, current_weekday: int) -> tp.Tuple[int, int, int]:
    p_cfg = cfg['periodic_config']

    logging.info("Getting periodic alarm time...")
    start_time = get_time_dt_obj_from_time_str(p_cfg['start_time'])
    end_time = get_time_dt_obj_from_time_str(p_cfg['end_time'])
    hm_period = get_time_dt_obj_from_time_str(p_cfg['hm_period'])
    
    # if we pass the end-time by incrementing with period, just start at the next day
    if time + hm_period > end_time:
        new_weekday = get_weekday_from_period(cfg['day_period'], current_weekday)
        hour,minute = get_hour_minute_tuple_from_time_dt(start_time)
        return (new_weekday, hour, minute)
    else:
        new_weekday = current_weekday
        hour,minute = get_hour_minute_tuple_from_time_dt(time + hm_period)
        return (new_weekday, hour, minute)

def get_next_timed_alarm_time(cfg: dict, current_time: dict, pj: PiJuice) -> tp.Tuple[int, int, int]:
    logging.info("Getting timed alarm time...")
    prev_alarm = pj.rtcAlarm.GetAlarm()
    prev_alarm = f"{prev_alarm['data']['hour']}:{prev_alarm['data']['minute']}"

    prev_alarm_idx = -1

    try:
        prev_alarm_idx = cfg['timed_config'].index(prev_alarm)
    except Exception as e:
        logging.warning("Could not find previous alarm time in timed_config, comparing time instead")
        current_dt = timedelta(hours=current_time['hour'], minutes=current_time['minute'])
        for i, time in enumerate(cfg['timed_config']):
            hour,minute = get_hour_minute_tuple_from_str(time)
            # if the alarm time is smaller than current time, use that as previous time, 
            if timedelta(hours=hour, minutes=minute) < current_dt:
                prev_alarm_idx = i
            else:
                break
        
        # if we didn't find a smaller time, the current time is before the first alarm time, 
        # so set previous time to the last alarm index
        if prev_alarm_idx == -1:
            prev_alarm_idx = len(cfg['timed_config'])
    
    next_alarm_idx = (prev_alarm_idx + 1) % len(cfg['timed_config'])
    next_day_period = next_alarm_idx < prev_alarm_idx

    new_weekday = current_time['weekday']
    hour,minute = get_hour_minute_tuple_from_str(cfg['timed_config'][next_alarm_idx])
    
    if next_day_period:
        new_weekday = get_weekday_from_period(cfg['day_period'], current_time['weekday'])

    return (new_weekday, hour, minute)

def get_next_time_from_config_and_current_time(cfg: dict, current_time: dict, pj: PiJuice) -> tp.Tuple[int, int, int]:
    time = timedelta(hours=current_time['hour'], minutes=current_time['minute'])
    if cfg['periodic_photos']:
        return get_next_periodic_alarm_time(cfg, time, current_time['weekday'])
    else:
        return get_next_timed_alarm_time(cfg, current_time, pj)

def set_alarm_from_config(pj: PiJuice) -> bool:
    cfg = get_alarm_config()
    time_dict = pj.rtcAlarm.GetTime()['data']

    try:
        weekday, hour, minute = get_next_time_from_config_and_current_time(cfg, time_dict, pj)
        logging.info(f"Setting new alarm day, hour, minute to: {weekday}, {hour}, {minute}")
        ret = pj.rtcAlarm.SetAlarm({"weekday" : weekday, "hour" : hour, "minute" : minute})
        if ret['error'] != "NO_ERROR":
            raise Exception(ret['error'])

    except Exception as e:
        logging.warning(f"Failed to set new alarm time from config. Using hardcoded time. Error was: {e}")
        pj.rtcAlarm.SetAlarm({'hour' : 13, 'minute' : 0})
        return False
    
    return True

# called when program exits
def exit_handler():
    # Make sure wakeup_enabled and wakeup_on_charge have the correct values
    set_alarm_from_config(pj)
    pj.rtcAlarm.SetWakeupEnabled(True)
    #pj.power.SetWakeUpOnCharge(0)
    logging.shutdown()

def set_last_uploaded(upload_tracker: str, last_file: str):
    with open(upload_tracker, "w") as f:
        f.write(last_file)

# get last uploaded file
def get_last_uploaded(upload_tracker: str) -> float:
    try:
        with open(upload_tracker, "r") as f:
            return os.path.getmtime(f.readline())
    except Exception as e:
        logging.info("No upload tracker file found, possibly corrupt. Resync everything.")
        return 0

# get list of files to be uploaded
def get_files_to_upload(images_folder: str, last_uploaded_time: float) -> list:
    # Get a list of all images in the images_folder
    files = list(filter(os.path.isfile, glob.glob(f"{images_folder}/*.jpg")))
    # Sort them by time last modified
    files.sort(key=os.path.getmtime)
    # Filter them by whether they were created later than last_uploaded_time
    # only add them to the list if they are newer than the last uploaded file
    return list(filter(lambda x: os.path.getmtime(x) > last_uploaded_time, files))

# Function that checks if the rtc was reset (so lost power)
def is_rtc_time_sane(pj: PiJuice) -> bool:
    d = pj.rtcAlarm.GetTime()
    if int(d['data']['year']) < 2023:
        return False
    
    return True

# Function that checks rtc reset and syncs time from ntp server
# Can be used to automatically rectify picture names after power loss
def check_and_sync_rtc(pj: PiJuice) -> bool:
    if not is_rtc_time_sane(pj):
        logging.info("RTC date is before 2023, so it has been off for a while.")
        # enable time server sync
        os.system("sudo systemctl enable --now systemd-timesyncd")

        sync_success = False
        for i in range(10):
            res = subprocess.check_output(["timedatectl", "status"])
            if b'System clock synchronized: yes' in res:
                sync_success = True
        
        # disable time server sync
        os.system("sudo systemctl disable --now systemd-timesyncd")

        return sync_success
    
    return True
        

if __name__ == "__main__":
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

    get_charge = pj.status.GetChargeLevel()
    charge_str = ""

    if get_charge['error'] == "NO_ERROR":
        charge_str = f"Charge level: {get_charge['data']}%"
    else:
        charge_str = f"Error getting battery charge level: {get_charge['error']}"

    uuid = get_uuid()

    # Write statement to log
    logging.info(f'Hello! Raspberry Pi on battery power. {charge_str}. Taking picture!')

    img_folder = "/home/opaque/opaqueoceans/images"

    if not check_and_sync_rtc(pj):
        # If we turn on with a reset RTC, it is most likely daytime. 
        # Maybe just use the current time as the alarm time and make an image every day?
        logging.warn("RTC sync failed. Time is not reliable")
    else:
        print(f"Time is synced: current time is {str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))}")
    

    curDate = str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    new_file_name = f"{img_folder}/image{curDate}::{uuid}.jpg"

    os.system(f"/usr/bin/libcamera-still -o {new_file_name}")

    upload_tracker = f"{img_folder}/last_uploaded"

    # if internet, upload image
    if connect() == True:
        last_uploaded_time = get_last_uploaded(upload_tracker)

        files = get_files_to_upload(img_folder, last_uploaded_time)
        files_to_upload_str = ", ".join(files)

        print(f"Internet is connected! Files to be uploaded: {files_to_upload_str}.")

        # also log upload
        logging.info(f"Uploading files: {files_to_upload_str}.")
        last_file = ""
        for file in files:
            ret = os.system(f"/home/opaque/opaqueoceans/dropbox_uploader.sh upload {file} /")
            
            # high byte is os.system process return code (see https://docs.python.org/3/library/os.html#os.wait)
            exit_sig = (ret >> 8)

            # upload returned without error
            if exit_sig == 0:
                last_file = file
            else:
                logging.info("Uploading to dropbox failed. Retry next time internet connection is found.")
                break
        
        if last_file != "":
            set_last_uploaded(upload_tracker, last_file)

    else:
        print('no internet, uploading later')

    # check if there is a user logged on, if so stay on, if not, turn off
    # Keep Raspberry Pi running - THING TO DO WOULD BE HERE, WOULD TURN OFF AFTER THIS!
    if checkForUser() == False:
        sleep(time)
        
        # Make sure wakeup_enabled and wakeup_on_charge have the correct values
        pj.rtcAlarm.SetWakeupEnabled(True)
    #pj.power.SetWakeUpOnCharge(0)

        # Make sure power to the Raspberry Pi is stopped to not deplete
        # the battery
        pj.power.SetSystemPowerSwitch(0)
        pj.power.SetPowerOff(30)

        logging.info('Bye! shutting down now as time has elapsed')

        # Now turn off the system after 1 min
        
        os.system("sudo shutdown -P +1")
        logging.shutdown()

    atexit.register(exit_handler)