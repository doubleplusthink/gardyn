#!/bin/sh

NETWORK_DIR="/usr/local/network"
NETWORK_HANDLER_DIR="/usr/local/etc"
WIFI_DIR="/usr/local/etc/gardyn/wifi"
IOT_DIR="/usr/local/etc/gardyn/device"
FAILURE_LOCK="$NETWORK_DIR/connection_failure.lock"

if [ ! -d "$NETWORK_DIR" ]; then
  mkdir $NETWORK_DIR
  chmod 777 $NETWORK_DIR
fi

# check if pigpiod already run
if [ -f "$NETWORK_DIR/reset" ]
then
	# reset=`cat $NETWORK_DIR/reset`
	# if [ "$reset" = "reset" ]
	# then
	# 	bash $NETWORK_HANDLER_DIR/network_switch.sh NAT
	# 	rm 	$NETWORK_DIR/reset
	# 	echo "pending" >> $NETWORK_DIR/reset
	# fi
	systemctl start wifi-pairing
else
	if [ -f "$NETWORK_DIR/ssid" ] && [ -f "$NETWORK_DIR/passphrase" ]
	then
		SSID=`cat /usr/local/network/ssid`
		# output=`iwconfig 2>&1 | grep "SSID:\"$SSID\""`
		CURR=`iwgetid wlan0 --raw`
		if [ "$SSID" != "$CURR" ]
		then
			bash $NETWORK_HANDLER_DIR/network_switch.sh WIFI
		else
			systemctl stop wifi-pairing
		fi
	fi
fi

pid=`pgrep pigpiod`
if [ -z "$pid" ]; then
	sudo pigpiod
fi

iot=`systemctl is-active iot-controller.service`
if [ "$iot" != "active" ]; then
	systemctl start iot-controller.service
fi

conn=`systemctl is-active conn-string.service`
if [ "$conn" != "active" ]; then
	systemctl start conn-string.service
fi