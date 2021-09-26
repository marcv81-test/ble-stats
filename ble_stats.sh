#!/usr/bin/env bash

"$(dirname ${0})/venv/bin/python3" "$(dirname ${0})/ble_stats.py" --devices="$(dirname ${0})/devices.yml"
