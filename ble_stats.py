import argparse
import bluepy.btle
import yaml
import sys

ADTYPE_SERVICE_DATA = 0x16
UUID_MI_THERMOMETER = 0x181A
UUID_MI_SCALE = 0x181B


def uint16(hi, lo):
    return ((hi & 0xFF) << 8) + (lo & 0xFF)


def int16(hi, lo):
    i = uint16(hi, lo)
    if i & (1 << 15):
        i -= 1 << 16
    return i


def has_method(obj, name):
    return hasattr(obj, name) and callable(getattr(obj, name))


class BLEDevice:
    """Generic BLE device."""

    def __init__(self, config):
        assert "addr" in config
        assert "device" in config
        self.tags = {"addr": config["addr"], "device": config["device"]}
        if "tags" in config:
            for key, value in config["tags"].items():
                self.tags[key] = value

    def handle_advertisement(self, device):
        for adtype, _, value in device.getScanData():
            if adtype == ADTYPE_SERVICE_DATA and has_method(self, "parse_service_data"):
                yield from self.handle_service_data(value)

    def handle_service_data(self, value):
        value = [int(value[i : i + 2], 16) for i in range(0, len(value), 2)]
        uuid = uint16(value[1], value[0])
        payload = value[2:]
        for fields in self.parse_service_data(uuid, payload):
            yield self.tags, fields


class MiThermometer(BLEDevice):
    """Mi Thermometer running the pvvx firmware."""

    def __init__(self, config):
        super().__init__(config)

    def parse_service_data(self, uuid, payload):
        if uuid != UUID_MI_THERMOMETER or len(payload) != 15:
            return
        fields = {
            "temperature": int16(payload[7], payload[6]) / 100,
            "humidity": uint16(payload[9], payload[8]) / 100,
            "battery_volt": uint16(payload[11], payload[10]) / 1000,
            "battery_percent": payload[12],
        }
        yield fields


class MiScale(BLEDevice):
    """Mi Body Composition Scale 2."""

    def __init__(self, config):
        super().__init__(config)

    def parse_service_data(self, uuid, payload):
        if uuid != UUID_MI_SCALE or len(payload) != 13:
            return
        control = uint16(payload[1], payload[0])
        unit_pound = control & (1 << 0)
        unit_catty = control & (1 << 14)
        unit_kilogram = not (unit_pound or unit_catty)
        weight_ready = control & (1 << 13)
        impedance_ready = control & (1 << 9)
        fields = {}
        if weight_ready and unit_kilogram:
            fields["weight"] = uint16(payload[12], payload[11]) / 200
        if impedance_ready:
            fields["impedance"] = uint16(payload[10], payload[9])
        if len(fields) > 0:
            yield fields


def device_factory(config):
    assert "device" in config
    devices = {"mi_thermometer": MiThermometer, "mi_scale": MiScale}
    assert config["device"] in devices
    return devices[config["device"]](config)


class StatsDelegate(bluepy.btle.DefaultDelegate):
    def __init__(self, devices):
        bluepy.btle.DefaultDelegate.__init__(self)
        self.register_devices(devices)

    def register_devices(self, devices):
        self.devices_map = {}
        for config in devices:
            assert "addr" in config
            self.devices_map[config["addr"]] = device_factory(config)

    def handleDiscovery(self, device, _, is_new_data):
        if not (is_new_data and device.addr in self.devices_map):
            return
        for tags, fields in self.devices_map[device.addr].handle_advertisement(device):
            tags = ",".join("%s=%s" % (k, v) for k, v in tags.items())
            fields = ",".join("%s=%s" % (k, v) for k, v in fields.items())
            sys.stdout.write("bluetooth,%s %s\n" % (tags, fields))
            sys.stdout.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--devices", type=str)
    arguments = parser.parse_args()
    with open(arguments.devices) as f:
        configs = yaml.safe_load(f)
    scanner = bluepy.btle.Scanner().withDelegate(StatsDelegate(configs))
    scanner.scan(0, passive=True)
