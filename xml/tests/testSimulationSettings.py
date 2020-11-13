from lxml import etree
from typing import List, Tuple
import unittest

filename_list: List[Tuple[str, bool]] = [
    ('network', False),
    ('vehicle-types', True),
    ('vehicle-models', True),
    ('distributions', True),
    ('lane-usage', True),
    ('behavior', True),
    ('evaluation', False),
]


class SimulationSettingsConstants:
    ROOT_TAG = 'simulation-settings'
    VERSION_ATTR = 'version'
    RUN_COUNT_ATTR = 'run-count'
    FILES_TAG = 'files'
    ARCHIVE_TAG = 'archive'
    ARCHIVE_PATH_ATTR = 'path'
    ARCHIVE_TYPE_ATTR = 'type'
    SIM_TIMES_TAG = 'simulation-times'
    SIM_START_ATTR = 'simulation-start-time'
    SIM_TIMEZONE_ATTR = 'utc-offset'
    SIM_EVALUATION_LENGTH_ATTR = 'evaluation-length'
    SIM_SEED_LENGTH_ATTR = 'seed-length'
    SIM_TIME_STEPS_ATTR = 'time-steps-per-second'
    SEEDING_TAG = 'seeding'
    SEEDING_FIRST_SEED_ATTR = 'random-seed-first-run'
    SEEDING_SEED_INCREMENT_ATTR = 'random-seed-increment'


class CleanDocumentBase:  # abstract
    def __init__(self, input_choice_node: etree.ElementBase):
        ns_map = {"xsi": 'http://www.w3.org/2001/XMLSchema-instance'}

        self._document_root: etree.ElementBase = etree.Element(SimulationSettingsConstants.ROOT_TAG, {
            SimulationSettingsConstants.VERSION_ATTR: '1',
            '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': '../simulation-settings.xsd',
            SimulationSettingsConstants.RUN_COUNT_ATTR: '10',
        }, nsmap=ns_map)

        self._input_choice_node = input_choice_node
        self._document_root.append(input_choice_node)

        self._simulation_times_node = etree.SubElement(self._document_root, SimulationSettingsConstants.SIM_TIMES_TAG, {
            SimulationSettingsConstants.SIM_START_ATTR: '17:30:21',
            SimulationSettingsConstants.SIM_TIMEZONE_ATTR: '-5',
            SimulationSettingsConstants.SIM_EVALUATION_LENGTH_ATTR: 'PT1H',
            SimulationSettingsConstants.SIM_SEED_LENGTH_ATTR: 'PT15M',
            SimulationSettingsConstants.SIM_TIME_STEPS_ATTR: '10',
        })

        self._seeding_node = etree.SubElement(self._document_root, SimulationSettingsConstants.SEEDING_TAG, {
            SimulationSettingsConstants.SEEDING_FIRST_SEED_ATTR: '66',
            SimulationSettingsConstants.SEEDING_SEED_INCREMENT_ATTR: '100',
        })

    def print_document_to_console(self):
        print(etree.tostring(self._document_root,
                             xml_declaration=False, pretty_print=True, encoding='unicode'))

    def write_document_to_file(self, filename):
        fp = open(filename, 'w')
        fp.write(etree.tostring(self._document_root,
                                pretty_print=True, encoding='unicode'))
        fp.close()

    def validate(self) -> bool:
        xs_doc = etree.parse('../simulation-settings.xsd')
        xsd = etree.XMLSchema(xs_doc)
        document = etree.ElementTree(self._document_root)
        return xsd.validate(document)

    def get_root_node(self):
        return self._document_root

    def get_input_choice_node(self) -> etree.ElementBase:
        return self._input_choice_node

    def get_simulation_times_node(self) -> etree.ElementBase:
        return self._simulation_times_node

    def get_seeding_node(self) -> etree.ElementBase:
        return self._seeding_node


class CleanDocumentWithFiles(CleanDocumentBase):
    @staticmethod
    def create_files_node():
        node: etree.ElementBase = etree.Element(SimulationSettingsConstants.FILES_TAG, {})
        files_to_include = list(filter(lambda f: (f[1] is True), filename_list))
        for file in files_to_include:
            keyword = file[0]
            node.attrib[keyword] = keyword + '.xml'

        return node

    def __init__(self):
        super().__init__(CleanDocumentWithFiles.create_files_node())


class CleanDocumentWithArchive(CleanDocumentBase):
    @staticmethod
    def create_archive_node():
        node: etree.ElementBase = etree.Element(SimulationSettingsConstants.ARCHIVE_TAG, {
            SimulationSettingsConstants.ARCHIVE_PATH_ATTR: '/home/karina/file.zip',
            SimulationSettingsConstants.ARCHIVE_TYPE_ATTR: 'zip'
        })

        return node

    def __init__(self):
        super().__init__(CleanDocumentWithArchive.create_archive_node())


class TestsForMostSettings(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocumentWithArchive()

    def test_that_clean_document_validates(self):
        self.assertTrue(self._doc.validate())

    def test_that_version_is_required(self):
        node: etree.ElementBase = self._doc.get_root_node()
        node.attrib.pop(SimulationSettingsConstants.VERSION_ATTR)
        self.assertFalse(self._doc.validate())

    def test_version_values(self):
        node: etree.ElementBase = self._doc.get_root_node()
        test_tuples = [
            (0, False),
            (-1, False),
            (1, True),
            (2, False),
        ]
        for value, expected_result in test_tuples:
            node.attrib[SimulationSettingsConstants.VERSION_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_run_count_is_required(self):
        node: etree.ElementBase = self._doc.get_root_node()
        node.attrib.pop(SimulationSettingsConstants.RUN_COUNT_ATTR)
        self.assertTrue(self._doc.validate())

    def test_run_count_values(self):
        node: etree.ElementBase = self._doc.get_root_node()
        test_tuples = [
            (-1, False),
            (0, False),
            (1, True),
            (100, True),
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[SimulationSettingsConstants.RUN_COUNT_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_input_method_is_required(self):
        self._doc.get_root_node().remove(self._doc.get_input_choice_node())
        self.assertFalse(self._doc.validate())

    def test_that_sim_times_is_required(self):
        self._doc.get_root_node().remove(self._doc.get_simulation_times_node())
        self.assertFalse(self._doc.validate())

    def test_that_simulation_start_time_is_required(self):
        self._doc.get_simulation_times_node().attrib.pop(SimulationSettingsConstants.SIM_START_ATTR)
        self.assertFalse(self._doc.validate())

    def test_that_simulation_seed_time_is_required(self):
        self._doc.get_simulation_times_node().attrib.pop(SimulationSettingsConstants.SIM_SEED_LENGTH_ATTR)
        self.assertFalse(self._doc.validate())

    def test_that_simulation_evaluation_time_is_required(self):
        self._doc.get_simulation_times_node().attrib.pop(SimulationSettingsConstants.SIM_EVALUATION_LENGTH_ATTR)
        self.assertFalse(self._doc.validate())

    def test_that_some_simulation_attributes_are_optional(self):
        target_node: etree.ElementBase = self._doc.get_simulation_times_node()
        for attr_name in [
            SimulationSettingsConstants.SIM_TIMEZONE_ATTR, SimulationSettingsConstants.SIM_TIME_STEPS_ATTR
        ]:
            if attr_name in target_node.attrib:
                target_node.attrib.pop(attr_name)

            self.assertTrue(self._doc.validate())

    def test_time_values(self):
        target_node = self._doc.get_simulation_times_node()
        test_tuples = [
            ('00:00:00', True),
            ('23:00:00-00:30', True),
            ('03:00', False),
            ('4:00 PM', False),
            ('04:00:00 PM', False),
        ]
        for (value, expected_result) in test_tuples:
            target_node.attrib[SimulationSettingsConstants.SIM_START_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_duration_values(self):
        target_node = self._doc.get_simulation_times_node()

        def check_duration_values(attr_name: str) -> None:
            initial_value: str = target_node.attrib[attr_name]
            test_tuples = [('04:00', False),
                           ('P1H', False),
                           ('PT1H', True),
                           ('-PT1M', False),
                           ('PT1H33M00S', True)]
            for (value, expected_result) in test_tuples:
                target_node.attrib[attr_name] = value
                self.assertEqual(self._doc.validate(), expected_result)

            target_node.attrib[attr_name] = initial_value

        for attr in [
            SimulationSettingsConstants.SIM_EVALUATION_LENGTH_ATTR,
            SimulationSettingsConstants.SIM_SEED_LENGTH_ATTR,
        ]:
            check_duration_values(attr)

    def test_time_step_count_values(self):
        test_tuples = [
            (0, False),
            (-1, False),
            (1, True),
            (5, True),
            (100, True),
        ]
        for (value, expected_result) in test_tuples:
            self._doc.get_simulation_times_node().attrib[SimulationSettingsConstants.SIM_TIME_STEPS_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_seeding_is_required(self):
        self._doc.get_root_node().remove(self._doc.get_seeding_node())
        self.assertFalse(self._doc.validate())

    def test_that_seeding_attributes_are_optional(self):
        attrs = [
            SimulationSettingsConstants.SEEDING_FIRST_SEED_ATTR,
            SimulationSettingsConstants.SEEDING_SEED_INCREMENT_ATTR,
        ]
        for attr_name in attrs:
            if attr_name in self._doc.get_seeding_node().attrib:
                self._doc.get_seeding_node().attrib.pop(attr_name)

            self.assertTrue(self._doc.validate())

    def test_first_seed_attribute_values(self):
        test_tuples = [
            (0, True),
            (-2291, False),
            (2292, True),
            ('not a number', False)
        ]
        for (value, expected_result) in test_tuples:
            self._doc.get_seeding_node().attrib[SimulationSettingsConstants.SEEDING_FIRST_SEED_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_seed_increment_attribute_values(self):
        test_tuples = [
            (0, True),
            (-2291, True),
            (2292, True),
            ('not a number', False)
        ]
        for (value, expected_result) in test_tuples:
            self._doc.get_seeding_node().attrib[SimulationSettingsConstants.SEEDING_SEED_INCREMENT_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)


class TestsForArchiveVersion(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocumentWithArchive()

    def test_that_path_is_required(self):
        self._doc.get_input_choice_node().attrib.pop(SimulationSettingsConstants.ARCHIVE_PATH_ATTR)
        self.assertFalse(self._doc.validate())

    def test_that_type_is_required(self):
        self._doc.get_input_choice_node().attrib.pop(SimulationSettingsConstants.ARCHIVE_TYPE_ATTR)
        self.assertFalse(self._doc.validate())

    def test_type_values(self):
        test_tuples = [
            ('zip', True),
            ('gz', True),
            ('7z', True),
            ('other', False)
        ]
        for (value, expected_result) in test_tuples:
            self._doc.get_input_choice_node().attrib[SimulationSettingsConstants.ARCHIVE_TYPE_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_other_attributes_are_okay(self):
        self._doc.get_input_choice_node().attrib['other-attribute'] = 'other value'
        self.assertTrue(self._doc.validate())


class TestsForFilesVersion(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocumentWithFiles()

    def check_that_attribute_is_banned(self, attr_name: str):
        self._doc.get_input_choice_node().attrib[attr_name] = '~/hello'
        self.assertFalse(self._doc.validate())

    def check_that_attribute_is_optional(self, attr_name: str):
        target_node: etree.ElementBase = self._doc.get_input_choice_node()
        if attr_name not in target_node.attrib:
            target_node.attrib[attr_name] = '~/hello'

        self.assertTrue(self._doc.validate())

        target_node.attrib.pop(attr_name)
        self.assertTrue(self._doc.validate())

    def test_that_network_is_banned(self):
        self.check_that_attribute_is_banned('network')

    def test_that_vehicle_types_is_optional(self):
        self.check_that_attribute_is_optional('vehicle-types')

    def test_that_vehicle_models_is_optional(self):
        self.check_that_attribute_is_optional('vehicle-models')

    def test_that_distributions_is_optional(self):
        self.check_that_attribute_is_optional('distributions')

    def test_that_lane_usage_is_optional(self):
        self.check_that_attribute_is_optional('lane-usage')

    def test_that_behavior_is_optional(self):
        self.check_that_attribute_is_optional('behavior')

    def test_that_evaluation_is_banned(self):
        self.check_that_attribute_is_banned('evaluation')


if __name__ == '__main__':
    unittest.main()
