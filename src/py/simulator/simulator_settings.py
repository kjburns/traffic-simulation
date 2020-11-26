import isodate
from lxml import etree
from datetime import time, timezone, timedelta
from simulator import xml_validation
from i18n_l10n.temporary_i18n_bridge import Localization


class SimulationSettingsXmlNames:
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


class SimulatorSettings:
    _run_count: int
    _simulation_start_time: time
    _time_zone: timezone
    _evaluation_length: timedelta
    _seed_length: timedelta
    _time_steps_per_second: int
    _seed_first_run: int
    _seed_subsequent_runs: int

    @classmethod
    def process_file(cls, sim_settings_file_path: str):
        root_element: etree.ElementBase = etree.parse(sim_settings_file_path).getroot()

        # check validation
        xsd = etree.XMLSchema(etree.parse(xml_validation.XmlValidation.SIMULATION_SETTINGS_XSD))
        if not xsd.validate(root_element):
            raise RuntimeError(Localization.get_message('E0002', sim_settings_file_path))

        version_number: int = int(root_element.attrib[SimulationSettingsXmlNames.VERSION_ATTR])

        # changes in future versions go here, newest at top

        if version_number >= 1:
            if SimulationSettingsXmlNames.RUN_COUNT_ATTR in root_element.attrib:
                cls._run_count = int(root_element.attrib[SimulationSettingsXmlNames.RUN_COUNT_ATTR])
            else:
                cls._run_count = 1

            simulation_times_node: etree.ElementBase = root_element.find(SimulationSettingsXmlNames.SIM_TIMES_TAG)
            cls._simulation_start_time = isodate.isotime.parse_time(
                simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_START_ATTR])

            if SimulationSettingsXmlNames.SIM_TIMEZONE_ATTR in simulation_times_node.attrib:
                cls._time_zone = timezone(
                    offset=timedelta(
                        hours=int(simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_TIMEZONE_ATTR])
                    )
                )
            else:
                cls._time_zone = timezone(offset=timedelta(hours=0))

            cls._evaluation_length = \
                isodate.parse_duration(simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_EVALUATION_LENGTH_ATTR])
            cls._seed_length = \
                isodate.parse_duration(simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_SEED_LENGTH_ATTR])

            if SimulationSettingsXmlNames.SIM_TIME_STEPS_ATTR in simulation_times_node.attrib:
                cls._time_steps_per_second = int(simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_TIME_STEPS_ATTR])
            else:
                cls._time_steps_per_second = 10

            seeding_node: etree.ElementBase = root_element.find(SimulationSettingsXmlNames.SEEDING_TAG)
            if SimulationSettingsXmlNames.SEEDING_FIRST_SEED_ATTR in seeding_node.attrib:
                cls._seed_first_run = int(seeding_node.attrib[SimulationSettingsXmlNames.SEEDING_FIRST_SEED_ATTR])
            else:
                cls._seed_first_run = 73110

            if SimulationSettingsXmlNames.SEEDING_SEED_INCREMENT_ATTR in seeding_node.attrib:
                cls._seed_subsequent_runs = \
                    int(seeding_node.attrib[SimulationSettingsXmlNames.SEEDING_SEED_INCREMENT_ATTR])
            else:
                cls._seed_subsequent_runs = 10

    @classmethod
    def run_count(cls) -> int:
        return cls._run_count

    @classmethod
    def simulation_start_time(cls) -> time:
        return cls._simulation_start_time

    @classmethod
    def time_zone(cls) -> timezone:
        return cls._time_zone

    @classmethod
    def evaluation_length(cls) -> timedelta:
        return cls._evaluation_length

    @classmethod
    def seed_length(cls) -> timedelta:
        return cls._seed_length

    @classmethod
    def time_steps_per_second(cls) -> int:
        return cls._time_steps_per_second

    @classmethod
    def seed_for_run_number(cls, run_number: int) -> int:
        return cls._seed_first_run + (run_number - 1) * cls._seed_subsequent_runs


class _ArchiveFormats:
    ZIP: str = 'zip'
    SEVEN_Z: str = '7z'
