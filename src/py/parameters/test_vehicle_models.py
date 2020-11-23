import unittest
from lxml import etree
from parameters.vehicle_models import VehicleModel, VehicleModelConstants
from uuid import uuid4 as uuid
from parameters.units import LengthUnits
from simulator.SimulatorLoggerWrapper import SimulatorLoggerWrapper
import logging


class TestsForVehicleModels(unittest.TestCase):
    def setUp(self) -> None:
        self._family_car_feet: etree.ElementBase = etree.Element(VehicleModelConstants.MODEL_TAG, {
            VehicleModelConstants.UNIT_NAME_ATTR: 'family car',
            VehicleModelConstants.MODEL_UUID_ATTR: str(uuid()),
            VehicleModelConstants.UNIT_LENGTH_ATTR: '18.5',
            VehicleModelConstants.UNIT_WIDTH_ATTR: '7.5',
        })
        self._family_car_meters: etree.ElementBase = etree.Element(VehicleModelConstants.MODEL_TAG, {
            VehicleModelConstants.UNIT_NAME_ATTR: 'family car',
            VehicleModelConstants.MODEL_UUID_ATTR: str(uuid()),
            VehicleModelConstants.UNIT_WIDTH_ATTR: '2.2',
            VehicleModelConstants.UNIT_LENGTH_ATTR: '5.6',
        })
        self._nameless_feet: etree.ElementBase = etree.Element(VehicleModelConstants.MODEL_TAG, {
            VehicleModelConstants.MODEL_UUID_ATTR: str(uuid()),
            VehicleModelConstants.UNIT_LENGTH_ATTR: '16.2',
            VehicleModelConstants.UNIT_WIDTH_ATTR: '6.5',
        })
        self._family_car_with_rv: etree.ElementBase = etree.Element(VehicleModelConstants.MODEL_TAG, {
            VehicleModelConstants.MODEL_UUID_ATTR: str(uuid()),
            VehicleModelConstants.UNIT_LENGTH_ATTR: '19.0',
            VehicleModelConstants.UNIT_WIDTH_ATTR: '8.5',
            VehicleModelConstants.UNIT_ARTICULATION_POINT_ATTR: '18.5',
        })
        etree.SubElement(self._family_car_with_rv, VehicleModelConstants.TRAILER_TAG, {
            VehicleModelConstants.UNIT_LENGTH_ATTR: '32.0',
            VehicleModelConstants.UNIT_WIDTH_ATTR: '9.0',
            VehicleModelConstants.TRAILER_TOWING_POINT_ATTR: '0.25',
        })

    def test_values_of_name(self):
        self.assertEqual(VehicleModel(self._nameless_feet, LengthUnits.FEET).name, '')
        self.assertEqual(VehicleModel(self._family_car_feet, LengthUnits.FEET).name, 'family car')

    def test_values_of_length_metric(self):
        self.assertAlmostEqual(VehicleModel(self._family_car_meters, LengthUnits.METERS).length, 5.6)

    def test_values_of_length_english(self):
        self.assertAlmostEqual(VehicleModel(self._family_car_feet, LengthUnits.FEET).length,
                               LengthUnits.FEET.convert_to_base_units(18.5))
        self.assertAlmostEqual(VehicleModel(self._family_car_feet, LengthUnits.FEET).total_length,
                               LengthUnits.FEET.convert_to_base_units(18.5))
        self.assertAlmostEqual(VehicleModel(self._family_car_with_rv, LengthUnits.FEET).total_length,
                               LengthUnits.FEET.convert_to_base_units(50.25))

    def test_values_of_width_metric(self):
        self.assertAlmostEqual(VehicleModel(self._family_car_meters, LengthUnits.METERS).width, 2.2)
        self.assertAlmostEqual(VehicleModel(self._family_car_meters, LengthUnits.METERS).maximum_width, 2.2)

    def test_values_of_width_english(self):
        self.assertAlmostEqual(VehicleModel(self._family_car_feet, LengthUnits.FEET).width,
                               LengthUnits.FEET.convert_to_base_units(7.5))
        self.assertAlmostEqual(VehicleModel(self._family_car_with_rv, LengthUnits.FEET).maximum_width,
                               LengthUnits.FEET.convert_to_base_units(9.0))

    def test_values_of_articulation_point(self):
        self.assertAlmostEqual(VehicleModel(self._family_car_with_rv, LengthUnits.FEET).articulation_point,
                               LengthUnits.FEET.convert_to_base_units(18.5))
        self.assertIsNone(VehicleModel(self._family_car_feet, LengthUnits.FEET).articulation_point)

    def test_effects_of_no_articulation_point(self):
        with self.assertLogs(SimulatorLoggerWrapper.logger(), logging.WARNING):
            self._family_car_with_rv.attrib.pop(VehicleModelConstants.UNIT_ARTICULATION_POINT_ATTR)
            VehicleModel(self._family_car_with_rv, LengthUnits.FEET)

    def test_values_of_trailer(self):
        self.assertIsNone(VehicleModel(self._family_car_feet, LengthUnits.FEET).trailer)
        self.assertIsNotNone(VehicleModel(self._family_car_with_rv, LengthUnits.FEET).trailer)

    def test_values_of_towing_point(self):
        self.assertAlmostEqual(VehicleModel(self._family_car_with_rv, LengthUnits.FEET).trailer.towing_point,
                               LengthUnits.FEET.convert_to_base_units(0.25))


if __name__ == '__main__':
    unittest.main()
