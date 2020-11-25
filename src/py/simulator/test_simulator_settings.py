import unittest
import isodate
from lxml import etree


class _ArchiveFormats:
    ZIP: str = 'zip'
    SEVEN_Z: str = '7z'


def _create_network_file_data() -> etree.ElementBase:
    pass


def _create_archive_file(fmt: _ArchiveFormats) -> str:
    """
    Creates a temporary archive file for use in testing. The file must be deleted manually when finished with it.
    Returns:
        name of the temporary archive file
    """
    # just putting a dummy call here for now to show the order of dependency
    _create_network_file_data()
    pass


class TestsForSimulatorSettings(unittest.TestCase):
    def test_that_default_values_load(self): pass

    def test_that_coded_values_load(self): pass

    def test_that_load_fails_with_improper_xml(self): pass

    def test_that_time_zones_are_handled_properly(self): pass


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
