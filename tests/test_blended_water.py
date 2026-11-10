"""Run with python -m unittest discover -s tests in a Home Assistant environment."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import Mock, patch

from custom_components.bwt_perla import sensor

API_KEY = "BlendedWaterSinceSetup_l"
TRANSLATION_KEY = "blended_water_since_setup"
UNIQUE_ID = f"test-entry_{API_KEY}"
TRANSLATIONS = Path(sensor.__file__).parent / "translations"


class BlendedWaterSensorTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.coordinator = SimpleNamespace(data={"WaterSinceSetup_l": 123})
        self.entry = SimpleNamespace(entry_id="test-entry")
        hass = SimpleNamespace(data={sensor.DOMAIN: {self.entry.entry_id: self.coordinator}})
        self.registry = Mock()
        add_entities = Mock()

        with patch.object(sensor.er, "async_get", return_value=self.registry):
            await sensor.async_setup_entry(hass, self.entry, add_entities)

        entities = add_entities.call_args.args[0]
        (self.entity,) = [entity for entity in entities if entity.unique_id == UNIQUE_ID]

    async def test_missing_field_does_not_prevent_registration(self):
        calls = [
            call.kwargs for call in self.registry.async_get_or_create.call_args_list
            if call.kwargs["unique_id"] == UNIQUE_ID
        ]
        self.assertEqual(calls, [{
            "domain": "sensor",
            "platform": sensor.DOMAIN,
            "unique_id": UNIQUE_ID,
            "suggested_object_id": "bwt_perla_blended_water_since_setup",
            "config_entry": self.entry,
        }])
        self.assertIsNone(self.entity.native_value)

    async def test_readings_can_appear_and_disappear_after_setup(self):
        for value, expected in [(0, 0), ("456", 456), (None, None), ("", None), ("invalid", None)]:
            with self.subTest(value=value):
                self.coordinator.data[API_KEY] = value
                self.assertEqual(self.entity.native_value, expected)
        del self.coordinator.data[API_KEY]
        self.assertIsNone(self.entity.native_value)

    async def test_sensor_metadata_and_translation_key(self):
        self.assertEqual(self.entity.translation_key, TRANSLATION_KEY)
        self.assertEqual(self.entity.device_class, sensor.SensorDeviceClass.WATER)
        self.assertEqual(self.entity.state_class, sensor.SensorStateClass.TOTAL_INCREASING)
        self.assertEqual(self.entity.native_unit_of_measurement, sensor.UnitOfVolume.LITERS)


class BlendedWaterTranslationsTest(TestCase):
    def test_localized_names(self):
        names = {
            "en": "Blended water since setup",
            "de": "Gemischtes Wasser seit Einrichtung",
            "da": "Blandet vand siden opsætning",
        }
        for language, expected in names.items():
            with self.subTest(language=language):
                data = json.loads((TRANSLATIONS / f"{language}.json").read_text(encoding="utf-8"))
                self.assertEqual(data["entity"]["sensor"][TRANSLATION_KEY]["name"], expected)
