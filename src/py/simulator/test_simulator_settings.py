import unittest
from lxml import etree
from network.NetworkXml import NetworkXmlNames, RoadXmlNames
from simulator.simulator_settings import SimulationSettingsXmlNames, SimulatorSettings, _ArchiveFormats
from parameters.units import LengthUnits, SpeedUnits
from uuid import uuid4 as uuid
import tempfile
import os
import zipfile
import isodate
from datetime import datetime, time, timezone


def _create_network_file_data() -> etree.ElementBase:
    root_node: etree.ElementBase = etree.Element(NetworkXmlNames.ROOT_TAG, {
        NetworkXmlNames.LAYOUT_UNITS_ATTR: LengthUnits.FEET.name,
        NetworkXmlNames.SPEED_UNITS_ATTR: SpeedUnits.MILES_PER_HOUR.name,
        NetworkXmlNames.VERSION_ATTR: '1',
    })
    roads_node: etree.ElementBase = etree.SubElement(root_node, RoadXmlNames.COLLECTION_TAG, {})
    road_node: etree.ElementBase = etree.SubElement(roads_node, RoadXmlNames.TAG, {
        RoadXmlNames.NAME_ATTR: 'Testing Drive',
        RoadXmlNames.UUID_ATTR: str(uuid()),
        RoadXmlNames.BEHAVIOR_ATTR: '29d9ce9f-e94b-4587-873f-aa1a5bf29ef5',
        RoadXmlNames.SPEED_LIMIT_ATTR: '40',
    })
    etree.SubElement(road_node, RoadXmlNames.CHAIN_TAG, {
        RoadXmlNames.CHAIN_POINTS_ATTR: '500,500 900,800'
    })
    lanes_node: etree.ElementBase = etree.SubElement(road_node, RoadXmlNames.LANES_COLLECTION_TAG, {})
    lane_node: etree.ElementBase = etree.SubElement(lanes_node, RoadXmlNames.LANE_TAG, {
        RoadXmlNames.LANE_ORDINAL_ATTR: '0',
        RoadXmlNames.LANE_WIDTH_ATTR: '12',
    })
    etree.SubElement(lane_node, RoadXmlNames.LANE_POLICY_TAG, {
        RoadXmlNames.LANE_POLICY_ID_ATTR: '6da1859e-ba54-4497-b356-a7ee95492330',
    })
    etree.SubElement(road_node, RoadXmlNames.POCKETS_COLLECTION_TAG, {})
    vehicle_entry_node: etree.ElementBase = etree.SubElement(road_node, RoadXmlNames.ENTRY_TAG, {})
    interval_node: etree.ElementBase = etree.SubElement(vehicle_entry_node, RoadXmlNames.ENTRY_INTERVAL_TAG, {
        RoadXmlNames.ENTRY_INTERVAL_START_ATTR: '17:00:00-05:00',
        RoadXmlNames.ENTRY_INTERVAL_END_ATTR: '17:15:00-05:00',
    })
    etree.ElementBase = etree.SubElement(interval_node, RoadXmlNames.ENTRY_INTERVAL_VEHICLE_TAG, {
        RoadXmlNames.ENTRY_INTERVAL_VEHICLE_TYPE_ATTR: '08ca86bd-88a4-4eef-b034-6303d02573fa',
        RoadXmlNames.ENTRY_INTERVAL_VEHICLE_COUNT_ATTR: '321',
    })

    return root_node


def _create_simulation_settings_data_with_defaults(file_element: etree.ElementBase) -> etree.ElementBase:
    root_node: etree.ElementBase = etree.Element(SimulationSettingsXmlNames.ROOT_TAG, {
        SimulationSettingsXmlNames.VERSION_ATTR: '1',
    })
    root_node.append(file_element)
    etree.SubElement(root_node, SimulationSettingsXmlNames.SIM_TIMES_TAG, {
        SimulationSettingsXmlNames.SIM_START_ATTR: '17:00:00-05:00',
        SimulationSettingsXmlNames.SIM_EVALUATION_LENGTH_ATTR: 'PT1H',
        SimulationSettingsXmlNames.SIM_SEED_LENGTH_ATTR: 'PT15M',
    })
    etree.SubElement(root_node, SimulationSettingsXmlNames.SEEDING_TAG, {})

    return root_node


def _create_simulation_settings_data_with_custom_values(file_element: etree.ElementBase) -> etree.ElementBase:
    root_node: etree.ElementBase = _create_simulation_settings_data_with_defaults(file_element)
    root_node.attrib[SimulationSettingsXmlNames.RUN_COUNT_ATTR] = '10'

    sim_times_node: etree.ElementBase = root_node.find(SimulationSettingsXmlNames.SIM_TIMES_TAG)
    sim_times_node.attrib[SimulationSettingsXmlNames.SIM_TIMEZONE_ATTR] = '-5'
    sim_times_node.attrib[SimulationSettingsXmlNames.SIM_TIME_STEPS_ATTR] = '15'

    seeding_node: etree.ElementBase = root_node.find(SimulationSettingsXmlNames.SEEDING_TAG)
    seeding_node.attrib[SimulationSettingsXmlNames.SEEDING_FIRST_SEED_ATTR] = '99'
    seeding_node.attrib[SimulationSettingsXmlNames.SEEDING_SEED_INCREMENT_ATTR] = '100'

    return root_node


def _create_archive_file(fmt: str) -> str:
    """
    Creates a temporary archive file for use in testing. The file must be deleted manually when finished with it.
    Returns:
        name of the temporary archive file
    """
    network_file_name: str
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        network_file_name = fp.name
        fp.write(etree.tostring(_create_network_file_data()))
        fp.close()

    if fmt == _ArchiveFormats.ZIP:
        zip_path: str
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            zip_path = fp.name
            fp.close()
        zip_file: zipfile.ZipFile = zipfile.ZipFile(zip_path, 'w')
        zip_file.write(network_file_name)
        os.remove(network_file_name)

        return zip_path
    elif fmt == _ArchiveFormats.SEVEN_Z:
        pass
    else:
        os.remove(network_file_name)
        return None


def _create_archive_node(filename: str, archive_format: str) -> etree.ElementBase:
    return etree.Element(SimulationSettingsXmlNames.ARCHIVE_TAG, {
        SimulationSettingsXmlNames.ARCHIVE_TYPE_ATTR: archive_format,
        SimulationSettingsXmlNames.ARCHIVE_PATH_ATTR: filename,
    })


def _write_temporary_file(data: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(bytes(data))
        fp.close()

        return fp.name


class TestsForSimulatorSettings(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_zip_location: str = _create_archive_file(_ArchiveFormats.ZIP)
        self._temp_ss_default_location: str = _write_temporary_file(
            etree.tostring(
                _create_simulation_settings_data_with_defaults(
                    _create_archive_node(self._temp_zip_location, _ArchiveFormats.ZIP)
                )
            )
        )
        self._temp_ss_custom_location: str = _write_temporary_file(
            etree.tostring(
                _create_simulation_settings_data_with_custom_values(
                    _create_archive_node(self._temp_zip_location, _ArchiveFormats.ZIP)
                )
            )
        )

    def tearDown(self) -> None:
        os.remove(self._temp_zip_location)
        os.remove(self._temp_ss_custom_location)
        os.remove(self._temp_ss_default_location)

    def test_that_default_values_load(self):
        # making sure the default values defined in the xsd are properly applied where appropriate
        SimulatorSettings.process_file(self._temp_ss_default_location)
        self.assertEqual(SimulatorSettings.run_count(), 1)
        self.assertEqual(SimulatorSettings.time_zone().utcoffset(None).seconds, 0)
        self.assertEqual(SimulatorSettings.time_steps_per_second(), 10)
        self.assertEqual(SimulatorSettings.seed_for_run_number(1), 73110)
        self.assertEqual(SimulatorSettings.seed_for_run_number(10), 73200)

    def test_that_coded_values_load(self):
        SimulatorSettings.process_file(self._temp_ss_custom_location)
        self.assertEqual(SimulatorSettings.run_count(), 10)
        self.assertEqual(SimulatorSettings.time_zone().utcoffset(None).seconds, 86400 - 5 * 3600)
        self.assertEqual(SimulatorSettings.time_steps_per_second(), 15)
        self.assertEqual(SimulatorSettings.seed_for_run_number(1), 99)
        self.assertEqual(SimulatorSettings.seed_for_run_number(10), 999)
        self.assertEqual(SimulatorSettings.simulation_start_time(), isodate.parse_time('17:00:00-05:00'))
        self.assertEqual(SimulatorSettings.evaluation_length(), isodate.parse_duration('PT1H'))
        self.assertEqual(SimulatorSettings.seed_length(), isodate.parse_duration('PT15M'))

    def test_that_load_fails_with_improper_xml(self):
        bad_file_xml = _create_simulation_settings_data_with_defaults(etree.Element('invalid', {}))
        file_path = _write_temporary_file(etree.tostring(bad_file_xml))

        def thrower():
            SimulatorSettings.process_file(file_path)

        self.assertRaises(RuntimeError, thrower)

        os.remove(file_path)

    def test_that_time_zones_are_handled_properly(self):
        SimulatorSettings.process_file(self._temp_ss_default_location)
        local_time: datetime = datetime.combine(
            datetime.today(),
            SimulatorSettings.simulation_start_time(),
            SimulatorSettings.simulation_start_time().tzinfo
        ).astimezone(SimulatorSettings.time_zone())
        self.assertEqual(local_time.time(), isodate.parse_time('22:00:00'))


class TestsForSimulatorSettingsWithFiles(unittest.TestCase):
    def test_that_default_vehicle_types_load(self): pass

    def test_that_default_vehicle_models_load(self): pass

    def test_that_default_distributions_load(self): pass

    def test_that_default_lane_usage_loads(self): pass

    def test_that_default_lane_behavior_loads(self): pass


class TestsForSimulatorSettingsWithArchive(unittest.TestCase):
    def test_that_default_vehicle_types_load(self): pass

    def test_that_default_vehicle_models_load(self): pass

    def test_that_default_distributions_load(self): pass

    def test_that_default_lane_usage_loads(self): pass

    def test_that_default_lane_behavior_loads(self): pass


if __name__ == '__main__':
    unittest.main()
