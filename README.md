# Intro

This project outputs Bluetooth Low Energy (BLE) sensors data in InfluxDB line protocol format. It integrates nicely with the Telegraf execd input plugin.

Supported sensors
- Xiaomi Thermometers running the pvvx firmware (https://github.com/pvvx/ATC_MiThermometer)
- Xiaomi Body Composition Scale 2

# Output

A sample follows.

    bluetooth,addr=a4:c1:38:d3:c0:6a,device=mi_thermometer temperature=26.51,humidity=82.69,battery_volt=3.005,battery_percent=89
    bluetooth,addr=5c:ca:d3:ed:7f:27,device=mi_scale weight=64.7,impedance=403

# Installation

Clone the project.

    git clone https://github.com/marcv81/ble-stats.git

Install the dependencies.

    cd ble-stats
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt

Run the unit tests.

    python3 -m unittest discover

Add the following to `/etc/sudoers.d/telegraf`.

    telegraf ALL=(root) NOPASSWD: /home/ubuntu/ble-stats/ble_stats.sh

Create `/etc/telegraf/telegraf.d/ble-stats.conf`.

    [[inputs.execd]]
      command = ["/usr/bin/sudo", "/home/ubuntu/ble-stats/ble_stats.sh"]
      signal = "none"
      data_format = "influx"
