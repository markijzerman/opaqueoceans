#!/usr/bin/python3

import subprocess, os
import atexit
import logging
from time import sleep
from pijuice import PiJuice

import glob

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
    pj.rtcAlarm.SetAlarm({'minute_period': 6})
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
def get_files_to_upload(images_folder: str) -> list:
    files = list(filter(os.path.isfile, glob.glob(f"{images_folder}/*.jpg")))
    files.sort(key=os.path.getmtime)
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
    
    return False
        

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

    # Write statement to log
    logging.info(f'Hello! Raspberry Pi on battery power. {charge_str}. Taking picture!')

    img_folder = "/home/opaque/opaqueoceans/images"

    curDate = str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    new_file_name = f"{img_folder}/image{curDate}.jpg"

    os.system(f"/usr/bin/libcamera-still -o {new_file_name}")

    upload_tracker = f"{img_folder}/last_uploaded"

    # if internet, upload image
    if connect() == True:
        last_uploaded_time = get_last_uploaded(upload_tracker)

        files = get_files_to_upload(img_folder)
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