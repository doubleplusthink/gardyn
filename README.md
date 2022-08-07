# Gardyn

## rc.local
- rc.local is the script that will be exec from reboot.
- It also will be triggered if network env is changed.

## network_checker.sh
- network_checker is a job in cront, it will run every 30 sec to check the network connectivity
- If the ssid and passphrase is set up but network connection is not corrected, it will trigger the rc.local to switch the network env.

