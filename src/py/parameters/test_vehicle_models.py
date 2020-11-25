import unittest
from lxml import etree
from parameters.vehicle_models import VehicleModel, VehicleModelConstants, VehicleModelCollection, process_file
from uuid import uuid4 as uuid
from parameters.units import LengthUnits
from simulator.SimulatorLoggerWrapper import SimulatorLoggerWrapper
import logging
from typing import List
from tempfile import NamedTemporaryFile
import os


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


class TestsForCollection(unittest.TestCase):
    @staticmethod
    def create_empty_document() -> etree.ElementBase:
        root: etree.ElementBase = etree.Element(VehicleModelConstants.ROOT_TAG, {
            VehicleModelConstants.COLLECTION_UNITS_ATTR: LengthUnits.FEET.name,
            VehicleModelConstants.COLLECTION_VERSION_ATTR: '1',
        })

        return root

    @staticmethod
    def create_good_document() -> etree.ElementBase:
        ids: List[str] = [str(uuid()) for _ in range(4)]
        root: etree.ElementBase = TestsForCollection.create_empty_document()
        for i in range(4):
            etree.SubElement(root, VehicleModelConstants.MODEL_TAG, {
                VehicleModelConstants.MODEL_UUID_ATTR: ids[i],
                VehicleModelConstants.UNIT_NAME_ATTR: 'A car',
                VehicleModelConstants.UNIT_LENGTH_ATTR: '16',
                VehicleModelConstants.UNIT_WIDTH_ATTR: '8',
            })

        return root

    def setUp(self) -> None:
        self._empty_file = NamedTemporaryFile(delete=False)
        self._empty_document = self.create_empty_document()

        self._good_file = NamedTemporaryFile(delete=False)
        self._good_document = self.create_good_document()

    def tearDown(self) -> None:
        if not self._empty_file.closed:
            self._empty_file.close()
        if not self._good_file.closed:
            self._good_file.close()

        os.remove(self._empty_file.name)
        os.remove(self._good_file.name)

    def write_and_close_files(self):
        self._empty_file.write(etree.tostring(self._empty_document))
        self._good_file.write(etree.tostring(self._good_document))

        self._empty_file.close()
        self._good_file.close()

    def test_document_loading(self):
        self.write_and_close_files()

        def open_empty_file():
            process_file(self._empty_file.name)

        self.assertRaises(RuntimeError, open_empty_file)

        VehicleModelCollection.reset()
        process_file(self._good_file.name)
        self.assertEqual(len(VehicleModelCollection.keys()), 4)

        model_id = VehicleModelCollection.keys()[1]
        model: VehicleModel = VehicleModelCollection[model_id]
        self.assertEqual(model.uuid, model_id)

    def test_model_retrieval(self):
        def get_nonexistent_entry():
            return VehicleModelCollection[str(uuid())]

        self.write_and_close_files()
        VehicleModelCollection.reset()
        process_file(self._good_file.name)
        self.assertRaises(KeyError, get_nonexistent_entry)
        for key in VehicleModelCollection.keys():
            self.assertIsNotNone(VehicleModelCollection[key])


if __name__ == '__main__':
    unittest.main()
