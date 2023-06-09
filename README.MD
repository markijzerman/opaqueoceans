# OPAQUE OCEANS, DIM DATA

Readme file for the software folder for Opaque Oceans, Dim Data

Dolist:
- apt-get update/upgrade, and follow this for git setup: https://garywoodfine.com/setting-up-ssh-keys-for-github-access/
- Set up Pijuice - https://github.com/PiSupply/PiJuice
    - sudo apt-get install pijuice-base
    - see https://github.com/PiSupply/PiJuice/tree/master/Software#pijuice-cli
    - launch with pijuice_cli
    - voor juiste batterij geconfigureerd in battery profile (pj1200)
    - (in 'system task' 'min charge' aangezet op 10% & wakeup on charge)
    - check https://raspberrypi-guide.github.io/other/boot-automation-pijuice
    - for the systemd to work, please make sure the service waits for the camera like so: https://unix.stackexchange.com/questions/186899/how-to-wait-for-a-dev-video0-before-starting-a-service
    - then do this with provided service file https://www.thedigitalpictureframe.com/ultimate-guide-systemd-autostart-scripts-raspberry-pi/
    - set up for use over usb for easy data access in the field!(TODO) https://www.mickmake.com/post/headless-pi-zero-w-2-easy-ways-of-connecting-tutorial/
    - using libcamera-still for making pictures
    - use dropbox_uploader.sh to upload pictures to dropbox if internet is available.
    - added dtoverlay=i2c-rtc,ds1307 to config.txt as explained in  https://github.com/PiSupply/PiJuice/issues/472#issuecomment-594000025
    - helpful voor python pijuice operatie: https://github.com/PiSupply/PiJuice/blob/master/Software/README.md
    - set EEPROM address to 52 as in https://github.com/PiSupply/PiJuice/issues/689
    - enable "real" hwclock:
        - sudo apt-get remove fake-hwclock
        - sudo update-rc.d -f fake-hwclock remove
        - sudo systemctl disable --now fake-hwclock
        - Run sudo nano /lib/udev/hwclock-set and comment out these three lines:<br>
            ` #if [ -e /run/systemd/system ] ; then `<br>
            ` # exit 0 `<br>
            ` #fi `<br>
        - as well as: `/sbin/hwclock --rtc=$dev --systz`
    - set timezone to UTC:
        - sudo raspi-config -> localization -> timezone -> none of the above -> UTC
    - time online sync uitzetten: sudo systemctl disable --now systemd-timesyncd


## Config json format
The config json has the following keys:
- <b>alarm_config:</b> object; <br>
Configuration object for the wakeup alarm
- tbd
<br>

The alarm_config has the following keys:
- <b>day_period:</b> int;<br>
The period in days to wait until the pi wakes up again
- <b>periodic_photos:</b> bool;<br>
Whether the alarm config uses periodic hours for wakeup or specific times
- <b>periodic_config:</b> object;<br>
The config for periodic wakeup
- <b>timed_config:</b> array;<br>
The config for specifically timed wakeup
<br>

The periodic_config has the following keys:
- <b>start_time:</b> string;<br>
The earliest wakeup time/first wakeup time that is set for a new day
- <b>end_time:</b> string;<br>
The latest wakeup time/last possible alarm time for a day
- <b>hm_period</b> string;<br>
The hour/minute period the alarm should use to set itself with between start_time and end_time

All of these value use "hh:mm" format. The python code splits it on the colon and expects 24h time, no AM or PM

### Example json file
```
{
    "alarm_config" : {
        "day_period"    : 2,
        "periodic_photos" : true,
        "periodic_config" : {
            "start_time"    : "8:30",
            "end_time"      : "14:00",
            "hm_period"     : "2:30"
        },
        "timed_config" : ["8:30", "11:30", "12:00"]
    }
}
```

TODO:

