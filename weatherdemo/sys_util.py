import logging
import subprocess
import time


def get_public_ip_address():
    ips = subprocess.check_output(['hostname', '-I']).decode().split(' ')
    return ips[1].strip()


def write_hostapd_conf(ip_address):
    args = [
        'interface=wlan0',
        'bridge=br0',
        'ssid=SplunkAR ({})'.format(ip_address),
        'hw_mode=g',
        'channel=7',
        'wmm_enabled=0',
        'macaddr_acl=0',
        'auth_algs=1',
        'ignore_broadcast_ssid=0',
        'wpa=2',
        'wpa_passphrase=splunkARrocks',
        'wpa_key_mgmt=WPA-PSK',
        'wpa_pairwise=TKIP',
        'rsn_pairwise=CCMP'
    ]
    subprocess.run(['sudo', 'echo', '\n'.join(args), '>', '/etc/hostapd/hostapd.conf'], check=True)


def setup_ssid():
    for i in range(20):
        ip_address = get_public_ip_address()
        if not ip_address:
            logging.warning('Cannot read publicly accessible IP address yet')
            time.sleep(3)
            continue
        write_hostapd_conf(ip_address)
