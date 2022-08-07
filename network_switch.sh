#!/bin/sh
MODE=$1

remove_static_ip() {
	if grep -Fxq 'interface wlan0' /etc/dhcpcd.conf
	then
		sed -i 's/interface wlan0//g' /etc/dhcpcd.conf
		sed -i 's/static ip_address=192.168.4.1\/24//g' /etc/dhcpcd.conf
		sed -i 's/nohook wpa_supplicant//g' /etc/dhcpcd.conf
	fi
}

config_as_nat() {

	# stop the dnsmasq server
	echo 'stopping dnsmasq and hostapd and wpa_supplicant'
	systemctl stop dnsmasq
	systemctl stop hostapd
	pkill wpa_supplicant || true

	# change config for dhcpd
	echo 'change /etc/dhcpcd.conf'
	remove_static_ip
	echo 'interface wlan0' >> /etc/dhcpcd.conf
	echo 'static ip_address=192.168.4.1/24' >> /etc/dhcpcd.conf
	echo 'nohook wpa_supplicant' >> /etc/dhcpcd.conf

	# start dhcp service
	echo 'starting dhcpd'
	service dhcpcd restart

	# config dnsmasq
	echo 'configing dnsmasq'
	if [ -f "/etc/dnsmasq.conf.orig" ]
	then
		rm /etc/dnsmasq.conf
	else
		mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
	fi
	echo 'interface=wlan0' >> /etc/dnsmasq.conf
	echo '  dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h' >> /etc/dnsmasq.conf

	# find the usable SSID
	# counter=0 
	#wlan=`iwlist wlan0 scanning essid "RaspGardyn"`
	#while [ -z "$wlan" ]
	#do
	#	counter=`expr $counter + 1`
	#	wlan=`iwlist wlan0 scanning essid "RaspGardyn$counter"`
	#done

	# find the serial number of rasp device
	serial=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | md5sum | cut -d ' ' -f 1 | tail -c 5`
	wlan="Gardyn$serial"

	# config hostapd
	echo 'editing /etc/default/hostapd'
	sed -i '/DAEMON_CONF=/s/DAEMON_CONF=".*"/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/g' /etc/default/hostapd
	if [ -f "/etc/hostapd/hostapd.conf" ]
	then
		rm /etc/hostapd/hostapd.conf
	fi
	echo "interface=wlan0
driver=nl80211
ssid=$wlan
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
#wpa=2
#wpa_passphrase=Spring2018
#wpa_key_mgmt=WPA-PSK
#wpa_pairwise=TKIP
#rsn_pairwise=CCMP
" >> /etc/hostapd/hostapd.conf
	# start hostapd and dnsmasq
	systemctl start hostapd
	systemctl start dnsmasq

	# add routing and masquerade
	echo 'editing /etc/sysctl.conf'
	sed -i '/net.ipv4.ip_forward=1/s/^#//g' /etc/sysctl.conf

	iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
	sh -c "iptables-save > /etc/iptables.ipv4.nat"
	iptables-restore < /etc/iptables.ipv4.nat
}

connect_wifi() {
	ssid=`cat /usr/local/network/ssid`
	passphrase=`cat /usr/local/network/passphrase`
    echo 'stopping wpa_supplicant'
    pkill wpa_supplicant
    sleep 1s
	echo 'stopping dnsmasq and hostapd'
	systemctl stop dnsmasq
	systemctl stop hostapd
	echo 'removing dhcpd conf'
	remove_static_ip
	if [ -f "/etc/wpa_supplicant/wpa_supplicant.conf" ]
	then
		rm /etc/wpa_supplicant/wpa_supplicant.conf
	fi
	echo 'restarting dhcp server'
	echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid=\"$ssid\"
    psk=\"$passphrase\"
}" >> /etc/wpa_supplicant/wpa_supplicant.conf
	service dhcpcd restart
	wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf
}

if [ "$MODE" = "NAT" ]
then
    config_as_nat
elif [ "$MODE" = "WIFI" ] && [ -f "/usr/local/network/ssid" ] && [ -f "/usr/local/network/passphrase" ]
then
    connect_wifi
fi