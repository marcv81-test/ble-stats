import ble_stats
import unittest


class TestMiThermometer(unittest.TestCase):
    def test(self):
        config = {"device": "mi_thermometer", "addr": "01:23:45:67:89:ab"}
        device = ble_stats.device_factory(config)
        value = "1a1857ed8f38c1a4ec0903112b0c640a04"
        counter = 0
        for _, fields in device.handle_service_data(value):
            self.assertEqual(fields["temperature"], 25.4)
            self.assertEqual(fields["humidity"], 43.55)
            self.assertEqual(fields["battery_volt"], 3.115)
            self.assertEqual(fields["battery_percent"], 100)
            counter += 1
        self.assertEqual(counter, 1)


class TestMiScale(unittest.TestCase):
    def test_1(self):
        """Both weight and impedance are available."""
        config = {"device": "mi_scale", "addr": "01:23:45:67:89:ab"}
        device = ble_stats.device_factory(config)
        value = "1b180226b207010100362bba01ec31"
        counter = 0
        for _, fields in device.handle_service_data(value):
            self.assertEqual(fields["weight"], 63.9)
            self.assertEqual(fields["impedance"], 442)
            counter += 1
        self.assertEqual(counter, 1)

    def test_2(self):
        """Weight is availble, impedance is not available."""
        config = {"device": "mi_scale", "addr": "01:23:45:67:89:ab"}
        device = ble_stats.device_factory(config)
        value = "1b180224b207010100362bfeffec31"
        counter = 0
        for _, fields in device.handle_service_data(value):
            self.assertEqual(fields["weight"], 63.9)
            self.assertFalse("impedance" in fields)
            counter += 1
        self.assertEqual(counter, 1)

    def test_3(self):
        """Neither weight nor impedance is available."""
        config = {"device": "mi_scale", "addr": "01:23:45:67:89:ab"}
        device = ble_stats.device_factory(config)
        value = "1b180284b207010100363900001400"
        counter = 0
        for _, _ in device.handle_service_data(value):
            counter += 1
        self.assertEqual(counter, 0)
