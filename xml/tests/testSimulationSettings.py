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

        self._input_choice_node = self._document_root.append(input_choice_node)

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
        self._doc.print_document_to_console()
        self.assertTrue(self._doc.validate())

    def test_that_version_is_required(self): pass

    def test_version_values(self): pass

    def test_that_run_count_is_required(self): pass

    def test_run_count_values(self): pass

    def test_that_input_method_is_required(self): pass

    def test_that_sim_times_is_required(self): pass

    def test_that_sim_attributes_are_required(self): pass

    def test_time_values(self): pass

    def test_duration_values(self): pass

    def test_time_step_count_values(self): pass

    def test_that_seeding_is_required(self): pass

    def test_that_seeding_attributes_are_required(self): pass

    def test_seeding_attribute_values(self): pass


if __name__ == '__main__':
    unittest.main()