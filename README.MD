# OPAQUE OCEANS, DIM DATA

Readme file for the software folder for Opaque Oceans, Dim Data

Dolist:
- Set up Pijuice - https://github.com/PiSupply/PiJuice
    - sudo apt-get install pijuice-base
    - see https://github.com/PiSupply/PiJuice/tree/master/Software#pijuice-cli
    - launch with pijuice_cli
    - voor juiste batterij geconfigureerd in battery profile (pj1200)
    - in 'system task' 'min charge' aangezet op 10% & wakeup on charge
    - meer info: https://www.youtube.com/watch?v=SRDBQTyQ8Ag&ab_channel=CoreElectronics
    - check https://raspberrypi-guide.github.io/other/boot-automation-pijuice
    - for the systemd to work, please make sure the service waits for the camera like so: https://unix.stackexchange.com/questions/186899/how-to-wait-for-a-dev-video0-before-starting-a-service
    - dataplicity installed for remote access


TODO:
- figure out connection over usb

