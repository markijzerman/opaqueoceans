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
    - time online sync uitzetten: systemctl disable systemd-timesyncd.service



TODO:
- figure out connection over usb ethernet

